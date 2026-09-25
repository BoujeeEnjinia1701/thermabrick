// ThermaBrick test article controller (ESP32, Arduino framework).
//
// Implements the five functions required by TBK-TST-001, section 1:
//   1. Charge mode: full power until T1 reaches the setpoint (550 C default), then PI on T1.
//   2. Hold mode:   PI on T1 at a lower setpoint (bake-out).
//   3. Blower:      fixed PWM duty, or closed-loop exchanger duty (W) from the airflow table.
//   4. Logging:     every channel, heater and blower duty at 10 s to a ring buffer, served
//                   as CSV over HTTP to the logging host (tools/logger.py).
//   5. Safe state:  heaters off after a reset (SSR pin pulled down), on T1 open, T1 > 575 C,
//                   sand > 560 C, loss of the logging host for 60 s, or a stalled main loop.
//
// The independent 600 C limit (REX-C100 and latching relay) is hardware and does not depend
// on this firmware.
//
// Licensed MIT (see LICENSE-SOFTWARE).
#include <Arduino.h>
#include <Preferences.h>
#include <WebServer.h>
#include <WiFi.h>
#include <esp_task_wdt.h>
#include <esp_timer.h>

#include "control.h"
#include "secrets.h"  // WIFI_SSID, WIFI_PASS, API_TOKEN (see include/secrets.example.h)

#ifndef TB_FW_REV
#define TB_FW_REV "unknown"
#endif

// ---------------------------------------------------------------- pins (TBK-PRC-002)
static const int PIN_SCK = 18;
static const int PIN_SO = 19;
static const int PIN_CS[5] = {5, 17, 16, 4, 22};   // T1, T3, T4, T5, T6
static const char* TC_NAME[5] = {"T1", "T3", "T4", "T5", "T6"};
enum { CH_T1 = 0, CH_T3, CH_T4, CH_T5, CH_T6 };
static const int PIN_SSR = 26;      // 10 kOhm pull-down to GND on the board
static const int PIN_BLOWER = 25;   // MOSFET module input, 10 kOhm pull-down
static const int BLOWER_LEDC_CH = 0;

// ---------------------------------------------------------------- timing
static const uint32_t TICK_MS = 1000;       // control and safety loop
static const uint32_t LOG_MS = 10000;       // log interval
static const int BURST_TICKS = 100;         // 1 s window of 10 ms ticks
static const uint32_t LOOP_STALL_MS = 6000; // output timer forces heaters off after this
static const int WDT_TIMEOUT_S = 8;

// ---------------------------------------------------------------- configuration (NVS)
struct Config {
    float v_line = 120.0f;       // measured line voltage, V
    float r_heat = 14.4f;        // four heaters in parallel, hot, Ohm
    float kp = 0.05f;            // heater PI, duty per K (full to zero over 20 K); tune in TP3
    float ti = 300.0f;           // heater PI, s
    float kpb = 0.002f;          // blower PI, duty per W
    float tib = 120.0f;          // blower PI, s
    float blower_min = 0.15f;    // lowest duty in power mode
    float off_t1 = 0.0f;         // T1 calibration offset, used for control and safety only
    uint32_t pwm_hz = 100;       // blower PWM frequency
    int air_n = 4;               // airflow table from TBK-TST-001 TP0 (duty 0..1 -> L/s)
    float air_duty[8] = {0.25f, 0.50f, 0.75f, 1.00f};
    float air_ls[8] = {1.0f, 2.0f, 3.0f, 4.0f};
} cfg;

Preferences prefs;

// ---------------------------------------------------------------- state
struct Channel {
    bool ok = false;
    bool open = false;
    float c = NAN;
};
Channel tc[5];

tb::HeaterController heater;
tb::Safety safety;
enum class BlowerMode : uint8_t { Off = 0, Duty = 1, Power = 2 };
BlowerMode blower_mode = BlowerMode::Off;
float blower_value = 0.0f;   // duty (0..1) or target W
float blower_duty = 0.0f;
tb::Pi blower_pi;

volatile float heater_duty = 0.0f;          // read by the output timer
volatile uint32_t loop_alive_ms = 0;
volatile bool loop_stalled = false;
float power_w = 0.0f, energy_wh = 0.0f, airflow_ls = 0.0f, exch_w = NAN;
uint32_t last_poll_ms = 0;
bool ever_polled = false;

// Log ring buffer: 3 h at 10 s
struct Row {
    uint32_t seq, t_s;
    float t[5];
    uint8_t hmode;
    float sp, hduty, p, e;
    uint8_t bmode;
    float bduty, v, q;
    uint16_t faults;
};
static const int RING = 1080;
Row ring[RING];
uint32_t seq = 0;

WebServer server(80);

// ---------------------------------------------------------------- MAX6675
// Bit-banged read, the same timing as the long-standing Adafruit driver. Each module needs
// at least 220 ms between reads; the loop reads every channel once per second.
static uint16_t max6675_read(int cs) {
    uint16_t v = 0;
    digitalWrite(cs, LOW);
    delayMicroseconds(10);
    for (int i = 15; i >= 0; --i) {
        digitalWrite(PIN_SCK, LOW);
        delayMicroseconds(10);
        if (digitalRead(PIN_SO)) v |= (1u << i);
        digitalWrite(PIN_SCK, HIGH);
        delayMicroseconds(10);
    }
    digitalWrite(cs, HIGH);
    return v;
}

static void read_thermocouples() {
    for (int k = 0; k < 5; ++k) {
        tb::TcReading r = tb::decode_max6675(max6675_read(PIN_CS[k]));
        tc[k].ok = r.ok;
        tc[k].open = r.open;
        tc[k].c = r.ok ? r.c : NAN;
    }
}

// ---------------------------------------------------------------- heater output timer
static int burst_tick = 0;
static void output_timer_cb(void*) {
    uint32_t now = millis();
    if ((uint32_t)(now - loop_alive_ms) > LOOP_STALL_MS) loop_stalled = true;
    int on_ticks = loop_stalled ? 0 : tb::burst_on_ticks(heater_duty, BURST_TICKS);
    digitalWrite(PIN_SSR, burst_tick < on_ticks ? HIGH : LOW);
    burst_tick = (burst_tick + 1) % BURST_TICKS;
}

// ---------------------------------------------------------------- blower
static void blower_write(float duty) {
    blower_duty = duty < 0 ? 0 : (duty > 1 ? 1 : duty);
    ledcWrite(BLOWER_LEDC_CH, (uint32_t)(blower_duty * 1023.0f + 0.5f));
}

static void blower_update(float dt) {
    airflow_ls = tb::interp(cfg.air_duty, cfg.air_ls, cfg.air_n, blower_duty);
    bool air_ok = tc[CH_T5].ok && tc[CH_T6].ok;
    exch_w = (air_ok && blower_duty > 0) ? tb::exchanger_duty_w(airflow_ls, tc[CH_T6].c, tc[CH_T5].c) : NAN;
    switch (blower_mode) {
        case BlowerMode::Off:
            blower_write(0);
            break;
        case BlowerMode::Duty:
            blower_write(blower_value);
            break;
        case BlowerMode::Power:
            if (!air_ok) break;   // hold the last duty until both air channels read again
            blower_write(blower_pi.update(blower_value - exch_w, dt, cfg.blower_min, 1.0f));
            break;
    }
}

// ---------------------------------------------------------------- config persistence
static void config_load() {
    prefs.begin("tb", true);
    cfg.v_line = prefs.getFloat("v_line", cfg.v_line);
    cfg.r_heat = prefs.getFloat("r_heat", cfg.r_heat);
    cfg.kp = prefs.getFloat("kp", cfg.kp);
    cfg.ti = prefs.getFloat("ti", cfg.ti);
    cfg.kpb = prefs.getFloat("kpb", cfg.kpb);
    cfg.tib = prefs.getFloat("tib", cfg.tib);
    cfg.blower_min = prefs.getFloat("bmin", cfg.blower_min);
    cfg.off_t1 = prefs.getFloat("off_t1", cfg.off_t1);
    cfg.pwm_hz = prefs.getUInt("pwm_hz", cfg.pwm_hz);
    if (prefs.isKey("air_n")) {
        cfg.air_n = prefs.getInt("air_n", cfg.air_n);
        prefs.getBytes("air_d", cfg.air_duty, sizeof(cfg.air_duty));
        prefs.getBytes("air_l", cfg.air_ls, sizeof(cfg.air_ls));
    }
    prefs.end();
}

static void config_save() {
    prefs.begin("tb", false);
    prefs.putFloat("v_line", cfg.v_line);
    prefs.putFloat("r_heat", cfg.r_heat);
    prefs.putFloat("kp", cfg.kp);
    prefs.putFloat("ti", cfg.ti);
    prefs.putFloat("kpb", cfg.kpb);
    prefs.putFloat("tib", cfg.tib);
    prefs.putFloat("bmin", cfg.blower_min);
    prefs.putFloat("off_t1", cfg.off_t1);
    prefs.putUInt("pwm_hz", cfg.pwm_hz);
    prefs.putInt("air_n", cfg.air_n);
    prefs.putBytes("air_d", cfg.air_duty, sizeof(cfg.air_duty));
    prefs.putBytes("air_l", cfg.air_ls, sizeof(cfg.air_ls));
    prefs.end();
}

// Parse "0.25:1.1,0.5:2.2,..." (duty 0..1 : L/s), ascending duty. Returns false if invalid.
static bool parse_air_table(const String& s) {
    float d[8], l[8];
    int n = 0, start = 0;
    while (start < (int)s.length() && n < 8) {
        int comma = s.indexOf(',', start);
        String pair = s.substring(start, comma < 0 ? s.length() : comma);
        int colon = pair.indexOf(':');
        if (colon < 0) return false;
        d[n] = pair.substring(0, colon).toFloat();
        l[n] = pair.substring(colon + 1).toFloat();
        if (d[n] <= 0 || d[n] > 1 || l[n] <= 0 || (n > 0 && (d[n] <= d[n - 1] || l[n] <= l[n - 1]))) return false;
        ++n;
        if (comma < 0) break;
        start = comma + 1;
    }
    if (n < 2) return false;
    cfg.air_n = n;
    for (int k = 0; k < n; ++k) {
        cfg.air_duty[k] = d[k];
        cfg.air_ls[k] = l[k];
    }
    return true;
}

// ---------------------------------------------------------------- logging
static const char* CSV_HEADER =
    "seq,t_s,T1_C,T3_C,T4_C,T5_C,T6_C,heater_mode,setpoint_C,heater_duty,heater_W,heater_Wh,"
    "blower_mode,blower_duty,airflow_Ls,exchanger_W,faults";

static void log_row() {
    Row& r = ring[seq % RING];
    r.seq = seq + 1;
    r.t_s = millis() / 1000;   // monotonic since boot; the host adds wall-clock time
    for (int k = 0; k < 5; ++k) r.t[k] = tc[k].c;
    r.hmode = (uint8_t)heater.mode;
    r.sp = heater.setpoint;
    r.hduty = heater_duty;
    r.p = power_w;
    r.e = energy_wh;
    r.bmode = (uint8_t)blower_mode;
    r.bduty = blower_duty;
    r.v = airflow_ls;
    r.q = exch_w;
    r.faults = safety.latched;
    ++seq;
    Serial.printf("%u,%u", r.seq, r.t_s);
    for (int k = 0; k < 5; ++k) Serial.printf(",%.2f", r.t[k]);
    Serial.printf(",%u,%.1f,%.3f,%.1f,%.2f,%u,%.3f,%.2f,%.1f,%u\n", r.hmode, r.sp, r.hduty, r.p, r.e, r.bmode,
                  r.bduty, r.v, r.q, r.faults);
}

static void fmt(String& out, float v, int dp) {
    out += ',';
    if (!isnan(v)) out += String(v, dp);   // blank field for an invalid reading
}

// ---------------------------------------------------------------- HTTP API
static bool authorized() {
    if (strlen(API_TOKEN) == 0) return true;
    if (server.arg("token") == API_TOKEN) return true;
    server.send(403, "text/plain", "forbidden\n");
    return false;
}

static void heartbeat() {
    last_poll_ms = millis();
    ever_polled = true;
}

static String status_json() {
    String j = "{\"fw\":\"" TB_FW_REV "\",\"uptime_s\":" + String(millis() / 1000);
    for (int k = 0; k < 5; ++k) {
        j += ",\"" + String(TC_NAME[k]) + "\":";
        j += tc[k].ok ? String(tc[k].c, 2) : (tc[k].open ? "\"open\"" : "\"fault\"");
    }
    j += ",\"heater_mode\":" + String((int)heater.mode) + ",\"setpoint\":" + String(heater.setpoint, 1);
    j += ",\"heater_duty\":" + String(heater_duty, 3) + ",\"heater_W\":" + String(power_w, 1);
    j += ",\"heater_Wh\":" + String(energy_wh, 2);
    j += ",\"blower_mode\":" + String((int)blower_mode) + ",\"blower_value\":" + String(blower_value, 3);
    j += ",\"blower_duty\":" + String(blower_duty, 3) + ",\"airflow_Ls\":" + String(airflow_ls, 2);
    j += ",\"exchanger_W\":" + (isnan(exch_w) ? String("null") : String(exch_w, 1));
    j += ",\"faults_latched\":" + String(safety.latched) + ",\"faults_active\":" + String(safety.active);
    j += ",\"seq\":" + String(seq) + "}";
    return j;
}

static void handle_status() {
    if (!authorized()) return;
    server.send(200, "application/json", status_json() + "\n");
}

// GET /log?since=N : header line, then every buffered row with seq > N (up to 360).
// Each call is also the heartbeat that keeps the heaters enabled.
static void handle_log() {
    if (!authorized()) return;
    heartbeat();
    uint32_t since = server.arg("since").toInt();
    uint32_t oldest = seq > RING ? seq - RING + 1 : 1;
    uint32_t from = since + 1 < oldest ? oldest : since + 1;
    String out = CSV_HEADER;
    out += '\n';
    int count = 0;
    for (uint32_t s = from; s <= seq && count < 360; ++s, ++count) {
        const Row& r = ring[(s - 1) % RING];
        out += String(r.seq) + ',' + String(r.t_s);
        for (int k = 0; k < 5; ++k) fmt(out, r.t[k], 2);
        out += ',' + String(r.hmode);
        fmt(out, r.sp, 1);
        fmt(out, r.hduty, 3);
        fmt(out, r.p, 1);
        fmt(out, r.e, 2);
        out += ',' + String(r.bmode);
        fmt(out, r.bduty, 3);
        fmt(out, r.v, 2);
        fmt(out, r.q, 1);
        out += ',' + String(r.faults) + '\n';
    }
    server.send(200, "text/csv", out);
}

// GET /heater?mode=off|charge|hold|manual&sp=550&duty=0.1
static void handle_heater() {
    if (!authorized()) return;
    String m = server.arg("mode");
    float sp = server.hasArg("sp") ? server.arg("sp").toFloat() : NAN;
    if (m == "off") {
        heater.set_mode(tb::HeaterMode::Off, heater.setpoint);
    } else if (m == "charge" || m == "hold") {
        float s = isnan(sp) ? (m == "charge" ? 550.0f : 200.0f) : sp;
        if (s < 20.0f || s > 550.0f) return (void)server.send(400, "text/plain", "sp must be 20 to 550\n");
        heater.set_mode(m == "charge" ? tb::HeaterMode::Charge : tb::HeaterMode::Hold, s);
    } else if (m == "manual") {
        float d = server.arg("duty").toFloat();
        if (d < 0.0f || d > 0.25f) return (void)server.send(400, "text/plain", "manual duty must be 0 to 0.25\n");
        heater.set_mode(tb::HeaterMode::Manual, heater.setpoint, d);
    } else {
        return (void)server.send(400, "text/plain", "mode must be off, charge, hold or manual\n");
    }
    handle_status();
}

// GET /blower?mode=off|duty|power&value=...
static void handle_blower() {
    if (!authorized()) return;
    String m = server.arg("mode");
    float v = server.arg("value").toFloat();
    if (m == "off") {
        blower_mode = BlowerMode::Off;
    } else if (m == "duty") {
        if (v < 0.0f || v > 1.0f) return (void)server.send(400, "text/plain", "duty must be 0 to 1\n");
        blower_mode = BlowerMode::Duty;
        blower_value = v;
    } else if (m == "power") {
        if (v <= 0.0f || v > 1000.0f) return (void)server.send(400, "text/plain", "power must be 1 to 1000 W\n");
        blower_mode = BlowerMode::Power;
        blower_value = v;
        blower_pi.kp = cfg.kpb;
        blower_pi.ti = cfg.tib;
        blower_pi.reset(blower_duty > cfg.blower_min ? blower_duty : cfg.blower_min, 0.0f);
    } else {
        return (void)server.send(400, "text/plain", "mode must be off, duty or power\n");
    }
    handle_status();
}

// GET /config : show. GET /config?key=value&... : set and save.
// Keys: v_line, r_heat, kp, ti, kpb, tib, bmin, off_t1, pwm_hz, air (e.g. 0.25:1.1,0.5:2.2)
static void handle_config() {
    if (!authorized()) return;
    bool changed = false;
    auto setf = [&](const char* key, float& dst, float lo, float hi) {
        if (!server.hasArg(key)) return true;
        float v = server.arg(key).toFloat();
        if (v < lo || v > hi) return false;
        dst = v;
        changed = true;
        return true;
    };
    bool ok = setf("v_line", cfg.v_line, 90, 140) && setf("r_heat", cfg.r_heat, 5, 50) && setf("kp", cfg.kp, 0, 1) &&
              setf("ti", cfg.ti, 10, 10000) && setf("kpb", cfg.kpb, 0, 0.1f) && setf("tib", cfg.tib, 5, 10000) &&
              setf("bmin", cfg.blower_min, 0, 0.8f) && setf("off_t1", cfg.off_t1, -5, 5);
    if (ok && server.hasArg("pwm_hz")) {
        uint32_t hz = server.arg("pwm_hz").toInt();
        if (hz < 20 || hz > 25000) ok = false;
        else {
            cfg.pwm_hz = hz;
            ledcSetup(BLOWER_LEDC_CH, cfg.pwm_hz, 10);
            changed = true;
        }
    }
    if (ok && server.hasArg("air")) {
        ok = parse_air_table(server.arg("air"));
        changed = changed || ok;
    }
    if (!ok) return (void)server.send(400, "text/plain", "value out of range\n");
    if (changed) config_save();
    heater.pi.kp = cfg.kp;
    heater.pi.ti = cfg.ti;
    String j = "{\"v_line\":" + String(cfg.v_line, 1) + ",\"r_heat\":" + String(cfg.r_heat, 2) +
               ",\"kp\":" + String(cfg.kp, 4) + ",\"ti\":" + String(cfg.ti, 0) + ",\"kpb\":" + String(cfg.kpb, 5) +
               ",\"tib\":" + String(cfg.tib, 0) + ",\"bmin\":" + String(cfg.blower_min, 2) +
               ",\"off_t1\":" + String(cfg.off_t1, 2) + ",\"pwm_hz\":" + String(cfg.pwm_hz) + ",\"air\":\"";
    for (int k = 0; k < cfg.air_n; ++k) j += (k ? "," : "") + String(cfg.air_duty[k], 2) + ":" + String(cfg.air_ls[k], 2);
    j += "\"}\n";
    server.send(200, "application/json", j);
}

// GET /clear : clear latched faults if no fault condition is present now.
static void handle_clear() {
    if (!authorized()) return;
    bool ok = safety.clear();
    if (ok) loop_stalled = false;   // the loop is running, since it is serving this request
    server.send(ok ? 200 : 409, "text/plain", ok ? "cleared\n" : "fault still present\n");
}

#ifdef TB_TEST_INJECT
// Test build only (env esp32dev_test): /inject?t1=600 overrides T1 for TBK-TST-001 TP1 step 5.
float inject_t1 = NAN;
static void handle_inject() {
    if (!authorized()) return;
    inject_t1 = server.hasArg("t1") ? server.arg("t1").toFloat() : NAN;
    server.send(200, "text/plain", isnan(inject_t1) ? "injection off\n" : "T1 injected\n");
}
#endif

// ---------------------------------------------------------------- setup and loop
void setup() {
    pinMode(PIN_SSR, OUTPUT);
    digitalWrite(PIN_SSR, LOW);
    Serial.begin(115200);
    pinMode(PIN_SCK, OUTPUT);
    digitalWrite(PIN_SCK, HIGH);
    pinMode(PIN_SO, INPUT);
    for (int k = 0; k < 5; ++k) {
        pinMode(PIN_CS[k], OUTPUT);
        digitalWrite(PIN_CS[k], HIGH);
    }
    config_load();
    heater.pi.kp = cfg.kp;
    heater.pi.ti = cfg.ti;
    ledcSetup(BLOWER_LEDC_CH, cfg.pwm_hz, 10);
    ledcAttachPin(PIN_BLOWER, BLOWER_LEDC_CH);
    blower_write(0);

    loop_alive_ms = millis();
    esp_timer_create_args_t targs = {};
    targs.callback = &output_timer_cb;
    targs.name = "ssr";
    esp_timer_handle_t timer;
    esp_timer_create(&targs, &timer);
    esp_timer_start_periodic(timer, 10000);   // 10 ms

    esp_task_wdt_init(WDT_TIMEOUT_S, true);
    esp_task_wdt_add(NULL);

    WiFi.mode(WIFI_STA);
    WiFi.setAutoReconnect(true);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    server.on("/status", handle_status);
    server.on("/log", handle_log);
    server.on("/heater", handle_heater);
    server.on("/blower", handle_blower);
    server.on("/config", handle_config);
    server.on("/clear", handle_clear);
#ifdef TB_TEST_INJECT
    server.on("/inject", handle_inject);
#endif
    server.begin();
    Serial.printf("# ThermaBrick test article firmware %s\n%s\n", TB_FW_REV, CSV_HEADER);
}

void loop() {
    static uint32_t last_tick = 0, last_log = 0;
    static bool wifi_reported = false;
    uint32_t now = millis();
    loop_alive_ms = now;
    esp_task_wdt_reset();
    server.handleClient();

    if (!wifi_reported && WiFi.status() == WL_CONNECTED) {
        Serial.printf("# connected, http://%s/status\n", WiFi.localIP().toString().c_str());
        wifi_reported = true;
    }

    if ((uint32_t)(now - last_tick) >= TICK_MS) {
        float dt = (now - last_tick) / 1000.0f;
        if (last_tick == 0) dt = TICK_MS / 1000.0f;
        last_tick = now;
        read_thermocouples();
        bool t1_ok = tc[CH_T1].ok;
        float t1 = tc[CH_T1].c + cfg.off_t1;
#ifdef TB_TEST_INJECT
        if (!isnan(inject_t1)) {
            t1_ok = true;
            t1 = inject_t1;
        }
#endif
        safety.evaluate(t1_ok, t1, tc[CH_T3].ok, tc[CH_T3].c, tc[CH_T4].ok, tc[CH_T4].c, now, last_poll_ms,
                        ever_polled);
        if (loop_stalled) safety.latched |= tb::F_LOOP;
        // Any latched fault drops the heater to Off, so clearing a fault never restarts heating.
        if (!safety.heaters_allowed() && heater.mode != tb::HeaterMode::Off)
            heater.set_mode(tb::HeaterMode::Off, heater.setpoint);
        heater_duty = heater.update(safety.heaters_allowed(), t1_ok, t1, dt);
        power_w = tb::heater_power_w(heater_duty, cfg.v_line, cfg.r_heat);
        energy_wh += power_w * dt / 3600.0f;
        blower_update(dt);
    }
    if ((uint32_t)(now - last_log) >= LOG_MS) {
        last_log = now;
        log_row();
    }
    delay(2);
}
