// ThermaBrick test article: control and safety logic. See control.h.
// Licensed MIT (see LICENSE-SOFTWARE).
#include "control.h"

namespace tb {

static float clampf(float v, float lo, float hi) { return v < lo ? lo : (v > hi ? hi : v); }

TcReading decode_max6675(uint16_t raw) {
    TcReading r{false, false, 0.0f};
    if (raw == 0x0000 || (raw & 0x8000) || (raw & 0x0002)) return r;  // missing module or bus fault
    if (raw & 0x0004) {
        r.open = true;
        return r;
    }
    r.ok = true;
    r.c = (raw >> 3) * 0.25f;
    return r;
}

float Pi::update(float err, float dt, float lo, float hi) {
    float p = kp * err;
    float di = (ti > 0.0f) ? kp * err * dt / ti : 0.0f;
    float out = p + i + di;
    // Integrate only if the output is not saturated, or if the error drives it back inside.
    if ((out < hi || di < 0.0f) && (out > lo || di > 0.0f)) i += di;
    i = clampf(i, lo, hi);
    return clampf(p + i, lo, hi);
}

void Pi::reset(float out, float err) { i = out - kp * err; }

void HeaterController::set_mode(HeaterMode m, float sp, float manual) {
    mode = m;
    setpoint = sp;
    manual_duty = clampf(manual, 0.0f, 1.0f);
    reached = false;
    pi.i = 0.0f;
}

float HeaterController::update(bool allowed, bool t1_ok, float t1, float dt) {
    if (!allowed || mode == HeaterMode::Off || !t1_ok) {
        pi.i = 0.0f;
        return 0.0f;
    }
    if (mode == HeaterMode::Manual) return manual_duty;
    float err = setpoint - t1;
    if (mode == HeaterMode::Charge && !reached) {
        if (err > 0.0f) return 1.0f;           // full power until the setpoint is first reached
        reached = true;
        pi.reset(1.0f, err);                   // bumpless handover to PI
    }
    return pi.update(err, dt, 0.0f, 1.0f);
}

void Safety::evaluate(bool t1_ok, float t1, bool t3_ok, float t3, bool t4_ok, float t4, uint32_t now_ms,
                      uint32_t last_poll_ms, bool ever_polled) {
    uint16_t a = 0;
    t1_bad = t1_ok ? 0 : t1_bad + 1;
    if (t1_bad >= lim.t1_bad_reads) a |= F_T1_INVALID;
    if (t1_ok && t1 > lim.t1_trip) a |= F_T1_HIGH;
    if ((t3_ok && t3 > lim.sand_trip) || (t4_ok && t4 > lim.sand_trip)) a |= F_SAND_HIGH;
    if (!ever_polled || (uint32_t)(now_ms - last_poll_ms) > lim.log_timeout_ms) a |= F_LOG_STALE;
    active = a;
    latched |= a;
}

bool Safety::clear() {
    if (active != 0) return false;
    latched = 0;
    return true;
}

int burst_on_ticks(float duty, int ticks_per_window) {
    int n = (int)(clampf(duty, 0.0f, 1.0f) * ticks_per_window + 0.5f);
    return n;
}

float interp(const float* x, const float* y, int n, float xq) {
    if (n <= 0) return 0.0f;
    if (n == 1 || xq <= x[0]) return y[0];
    if (xq >= x[n - 1]) return y[n - 1];
    for (int k = 1; k < n; ++k) {
        if (xq <= x[k]) {
            float f = (xq - x[k - 1]) / (x[k] - x[k - 1]);
            return y[k - 1] + f * (y[k] - y[k - 1]);
        }
    }
    return y[n - 1];
}

float interp_inverse(const float* x, const float* y, int n, float yq) { return interp(y, x, n, yq); }

float air_density(float t_c) { return 101325.0f / (287.05f * (t_c + 273.15f)); }

float exchanger_duty_w(float v_ls, float t_in_c, float t_out_c) {
    // Volume flow is calibrated at the inlet (room) temperature; cp at the mean air temperature.
    float m = air_density(t_in_c) * v_ls / 1000.0f;
    float tm = 0.5f * (t_in_c + t_out_c);
    float cp = 1002.0f + 0.12f * (tm - 20.0f);
    if (cp < 1005.0f) cp = 1005.0f;
    return m * cp * (t_out_c - t_in_c);
}

float heater_power_w(float duty, float v_line, float r_parallel) {
    if (r_parallel <= 0.0f) return 0.0f;
    return clampf(duty, 0.0f, 1.0f) * v_line * v_line / r_parallel;
}

}  // namespace tb
