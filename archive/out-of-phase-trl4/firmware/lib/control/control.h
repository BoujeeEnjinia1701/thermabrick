// ThermaBrick test article: control and safety logic.
//
// Pure C++ with no Arduino dependencies, so the same code runs on the ESP32 and in the
// native unit tests (test/test_control). Everything that decides whether the heaters may
// run lives here.
//
// Licensed MIT (see LICENSE-SOFTWARE).
#pragma once
#include <stdint.h>

namespace tb {

// ---------------------------------------------------------------- thermocouples
struct TcReading {
    bool ok;      // valid reading
    bool open;    // thermocouple open circuit (MAX6675 bit D2)
    float c;      // temperature, deg C (valid only when ok)
};

// Decode a raw 16-bit MAX6675 frame. Bit 15 is a dummy sign bit that always reads 0 and
// bit 1 is the device ID, also 0; a frame of 0x0000 or with either bit set means the
// module is missing or the bus is faulty, so it is rejected.
TcReading decode_max6675(uint16_t raw);

// ---------------------------------------------------------------- PI controller
// Parallel-form PI with conditional integration (no windup at the output limits).
struct Pi {
    float kp = 0.0f;   // output per unit error
    float ti = 1.0f;   // integral time, s
    float i = 0.0f;    // integral term, in output units

    float update(float err, float dt, float lo, float hi);
    void reset(float out = 0.0f, float err = 0.0f);  // bumpless: next output starts at `out`
};

// ---------------------------------------------------------------- heater control
enum class HeaterMode : uint8_t { Off = 0, Charge = 1, Hold = 2, Manual = 3 };

// Charge: full power until T1 first reaches the setpoint, then PI on T1 (TBK-TST-001 s.1).
// Hold:   PI on T1 from the start (bake-out).
// Manual: fixed duty, for commissioning checks only.
struct HeaterController {
    HeaterMode mode = HeaterMode::Off;
    float setpoint = 550.0f;
    float manual_duty = 0.0f;
    bool reached = false;   // charge mode: setpoint reached once
    Pi pi;

    void set_mode(HeaterMode m, float sp, float manual = 0.0f);
    // Returns heater duty 0..1. `allowed` is false whenever any fault is latched.
    float update(bool allowed, bool t1_ok, float t1, float dt);
};

// ---------------------------------------------------------------- safety
enum Fault : uint16_t {
    F_T1_INVALID = 1 << 0,  // T1 open or unreadable for several consecutive reads
    F_T1_HIGH = 1 << 1,     // T1 above the firmware trip (575 C)
    F_SAND_HIGH = 1 << 2,   // T3 or T4 above 560 C (quartz inversion margin)
    F_LOG_STALE = 1 << 3,   // no poll from the logging host within the timeout
    F_LOOP = 1 << 4,        // main loop stalled (set by the output timer)
};

struct SafetyLimits {
    float t1_trip = 575.0f;
    float sand_trip = 560.0f;
    uint32_t log_timeout_ms = 60000;
    int t1_bad_reads = 3;
};

struct Safety {
    SafetyLimits lim;
    uint16_t latched = 0;
    uint16_t active = 0;    // conditions present at the last evaluation
    int t1_bad = 0;

    // Evaluate on every 1 s tick. Faults latch until clear() succeeds.
    // `ever_polled` false means no logging host has connected since boot: heaters stay off.
    void evaluate(bool t1_ok, float t1, bool t3_ok, float t3, bool t4_ok, float t4, uint32_t now_ms,
                  uint32_t last_poll_ms, bool ever_polled);
    // Clears the latch only if no fault condition is present now. Returns true on success.
    bool clear();
    bool heaters_allowed() const { return latched == 0; }
};

// ---------------------------------------------------------------- burst firing
// Heater duty is applied as whole ticks in a fixed window (zero-cross SSR, 1 s window,
// 10 ms ticks). Returns how many ticks of the window are on.
int burst_on_ticks(float duty, int ticks_per_window);

// ---------------------------------------------------------------- airflow and duty
// Piecewise-linear lookup with clamping at both ends. x must be ascending.
float interp(const float* x, const float* y, int n, float xq);
// Inverse lookup: the x giving yq, assuming y ascending.
float interp_inverse(const float* x, const float* y, int n, float yq);

float air_density(float t_c);                                   // kg/m^3 at 101.325 kPa
float exchanger_duty_w(float v_ls, float t_in_c, float t_out_c);  // V measured at t_in
float heater_power_w(float duty, float v_line, float r_parallel);

}  // namespace tb
