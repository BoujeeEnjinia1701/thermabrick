// Host unit tests for the control and safety logic: pio test -e native
// Licensed MIT (see LICENSE-SOFTWARE).
#include <unity.h>

#include "control.h"

using namespace tb;

void setUp() {}
void tearDown() {}

// ---------------------------------------------------------------- MAX6675 decoding
void test_decode_valid() {
    TcReading r = decode_max6675((uint16_t)(2200 << 3));  // 2200 x 0.25 = 550 C
    TEST_ASSERT_TRUE(r.ok);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 550.0f, r.c);
}
void test_decode_open() {
    TcReading r = decode_max6675((uint16_t)((100 << 3) | 0x4));
    TEST_ASSERT_FALSE(r.ok);
    TEST_ASSERT_TRUE(r.open);
}
void test_decode_bus_faults() {
    TEST_ASSERT_FALSE(decode_max6675(0x0000).ok);   // module missing, MISO low
    TEST_ASSERT_FALSE(decode_max6675(0xFFFF).ok);   // MISO floating high
    TEST_ASSERT_FALSE(decode_max6675((100 << 3) | 0x2).ok);  // device ID bit set
}

// ---------------------------------------------------------------- heater control
void test_charge_full_power_until_setpoint() {
    HeaterController h;
    h.pi.kp = 0.05f;
    h.pi.ti = 300.0f;
    h.set_mode(HeaterMode::Charge, 550.0f);
    TEST_ASSERT_EQUAL_FLOAT(1.0f, h.update(true, true, 150.0f, 1.0f));
    TEST_ASSERT_EQUAL_FLOAT(1.0f, h.update(true, true, 549.0f, 1.0f));  // no early taper
    float d = h.update(true, true, 551.0f, 1.0f);                        // reached: PI takes over
    TEST_ASSERT_TRUE(h.reached);
    TEST_ASSERT_TRUE(d < 1.0f && d > 0.9f);                              // bumpless handover
}
void test_charge_tapers_and_holds() {
    HeaterController h;
    h.pi.kp = 0.05f;
    h.pi.ti = 300.0f;
    h.set_mode(HeaterMode::Charge, 550.0f);
    h.update(true, true, 551.0f, 1.0f);
    float d = 1.0f;
    for (int k = 0; k < 1200; ++k) d = h.update(true, true, 555.0f, 1.0f);  // 5 K over for 20 min
    TEST_ASSERT_FLOAT_WITHIN(1e-6f, 0.0f, d);
    for (int k = 0; k < 60; ++k) d = h.update(true, true, 548.0f, 1.0f);    // no windup: recovers
    TEST_ASSERT_TRUE(d > 0.0f);
}
void test_hold_is_proportional_from_start() {
    HeaterController h;
    h.pi.kp = 0.05f;
    h.pi.ti = 300.0f;
    h.set_mode(HeaterMode::Hold, 200.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.01f, 0.5f, h.update(true, true, 190.0f, 1.0f));
}
void test_heater_off_when_not_allowed_or_t1_bad() {
    HeaterController h;
    h.set_mode(HeaterMode::Charge, 550.0f);
    TEST_ASSERT_EQUAL_FLOAT(0.0f, h.update(false, true, 150.0f, 1.0f));
    TEST_ASSERT_EQUAL_FLOAT(0.0f, h.update(true, false, 150.0f, 1.0f));
    h.set_mode(HeaterMode::Manual, 550.0f, 0.1f);
    TEST_ASSERT_EQUAL_FLOAT(0.1f, h.update(true, true, 20.0f, 1.0f));
    TEST_ASSERT_EQUAL_FLOAT(0.0f, h.update(false, true, 20.0f, 1.0f));
}

// ---------------------------------------------------------------- safety
static Safety polled_ok() {
    Safety s;
    s.evaluate(true, 300, true, 250, true, 280, 1000, 1000, true);
    return s;
}
void test_no_host_blocks_heaters() {
    Safety s;
    s.evaluate(true, 300, true, 250, true, 280, 1000, 0, false);
    TEST_ASSERT_FALSE(s.heaters_allowed());
    TEST_ASSERT_TRUE(s.latched & F_LOG_STALE);
}
void test_log_timeout_latches() {
    Safety s = polled_ok();
    TEST_ASSERT_TRUE(s.heaters_allowed());
    s.evaluate(true, 300, true, 250, true, 280, 1000 + 60000, 1000, true);   // exactly 60 s: ok
    TEST_ASSERT_TRUE(s.heaters_allowed());
    s.evaluate(true, 300, true, 250, true, 280, 1000 + 61000, 1000, true);   // 61 s: fault
    TEST_ASSERT_FALSE(s.heaters_allowed());
    TEST_ASSERT_FALSE(s.clear());                                            // still stale
    s.evaluate(true, 300, true, 250, true, 280, 70000, 69000, true);         // host back
    TEST_ASSERT_FALSE(s.heaters_allowed());                                  // still latched
    TEST_ASSERT_TRUE(s.clear());
    TEST_ASSERT_TRUE(s.heaters_allowed());
}
void test_t1_high_and_sand_high() {
    Safety s = polled_ok();
    s.evaluate(true, 576, true, 250, true, 280, 2000, 2000, true);
    TEST_ASSERT_TRUE(s.latched & F_T1_HIGH);
    Safety u = polled_ok();
    u.evaluate(true, 540, true, 250, true, 561, 2000, 2000, true);
    TEST_ASSERT_TRUE(u.latched & F_SAND_HIGH);
    Safety v = polled_ok();
    v.evaluate(true, 540, false, 0, false, 0, 2000, 2000, true);            // sand channels lost: no trip
    TEST_ASSERT_TRUE(v.heaters_allowed());
}
void test_t1_invalid_after_three_reads() {
    Safety s = polled_ok();
    s.evaluate(false, 0, true, 250, true, 280, 2000, 2000, true);
    s.evaluate(false, 0, true, 250, true, 280, 3000, 3000, true);
    TEST_ASSERT_TRUE(s.heaters_allowed());                                   // two glitches tolerated
    s.evaluate(false, 0, true, 250, true, 280, 4000, 4000, true);
    TEST_ASSERT_TRUE(s.latched & F_T1_INVALID);
}

// ---------------------------------------------------------------- burst, lookup, physics
void test_burst_ticks() {
    TEST_ASSERT_EQUAL_INT(0, burst_on_ticks(0.0f, 100));
    TEST_ASSERT_EQUAL_INT(100, burst_on_ticks(1.0f, 100));
    TEST_ASSERT_EQUAL_INT(100, burst_on_ticks(1.7f, 100));
    TEST_ASSERT_EQUAL_INT(0, burst_on_ticks(-0.5f, 100));
    TEST_ASSERT_EQUAL_INT(25, burst_on_ticks(0.25f, 100));
}
void test_interp() {
    const float x[] = {0.25f, 0.5f, 1.0f};
    const float y[] = {1.0f, 2.0f, 4.0f};
    TEST_ASSERT_FLOAT_WITHIN(1e-5f, 1.0f, interp(x, y, 3, 0.1f));
    TEST_ASSERT_FLOAT_WITHIN(1e-5f, 3.0f, interp(x, y, 3, 0.75f));
    TEST_ASSERT_FLOAT_WITHIN(1e-5f, 4.0f, interp(x, y, 3, 2.0f));
    TEST_ASSERT_FLOAT_WITHIN(1e-5f, 0.75f, interp_inverse(x, y, 3, 3.0f));
}
void test_exchanger_duty() {
    // 2.8 L/s of 20 C air heated to 314 C is about 1 kW (TBK-CAL-001, section 4.2)
    TEST_ASSERT_FLOAT_WITHIN(40.0f, 1000.0f, exchanger_duty_w(2.8f, 20.0f, 314.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.5f, 1000.0f, heater_power_w(1.0f, 120.0f, 14.4f));
}

int main(int, char**) {
    UNITY_BEGIN();
    RUN_TEST(test_decode_valid);
    RUN_TEST(test_decode_open);
    RUN_TEST(test_decode_bus_faults);
    RUN_TEST(test_charge_full_power_until_setpoint);
    RUN_TEST(test_charge_tapers_and_holds);
    RUN_TEST(test_hold_is_proportional_from_start);
    RUN_TEST(test_heater_off_when_not_allowed_or_t1_bad);
    RUN_TEST(test_no_host_blocks_heaters);
    RUN_TEST(test_log_timeout_latches);
    RUN_TEST(test_t1_high_and_sand_high);
    RUN_TEST(test_t1_invalid_after_three_reads);
    RUN_TEST(test_burst_ticks);
    RUN_TEST(test_interp);
    RUN_TEST(test_exchanger_duty);
    return UNITY_END();
}
