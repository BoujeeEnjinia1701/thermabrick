---
doc_id: TBK-TST-001
title: ThermaBrick test article test plan
project: ThermaBrick
doc_type: Test plan
version: "0.5"
status: Draft
date: '2026-09-24'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-24'
  author: Amish Chadha
  change: Initial draft. Six test procedures for the reduced-scale test article, with instrumentation, uncertainty, analysis method, pass criteria, safety and schedule
- version: "0.2"
  date: '2026-09-24'
  author: Amish Chadha
  change: Firmware and logging host written (firmware/); section 1 now references them and lists the added sand trip; prerequisite checked off
- version: "0.3"
  date: '2026-09-24'
  author: Amish Chadha
  change: Analysis script written and checked on synthetic data. Section 9 adds a fitted heater power correction and defines the time-to-80 % and closure checks so they are independent of the fitted model state; TP3 pass wording and prerequisites updated
- version: "0.4"
  date: '2026-09-24'
  author: Amish Chadha
  change: Thermocouple tips moved from 245 mm to 300 mm above the drum floor, so the 500 mm probes end inside the top insulation (docs/07-build/cut-list.md, C4)
- version: "0.5"
  date: '2026-09-24'
  author: Amish Chadha
  change: Section 12 names the report template TBK-TST-002 and the script that fills its analysis sections
---

# ThermaBrick test article test plan

This plan tests the reduced-scale test article (TBK-PRC-002) in six procedures over about seven weeks. They measure the three properties the full-scale design rests on: the effective conductivity of the sand, the contact conductance at the well wall and the conductivity of the insulation. They also check the exchanger model, the safety limits and the drum's durability over 25 cycles. The measured values replace the literature values in `tbk_cal_001.py`, and TBK-CAL-001 is reissued with them before any money is committed to the full-scale build. Results go in test report TBK-TST-002.

| Procedure | Purpose | Objective (TBK-PRC-002) | Full-scale requirement informed | Duration |
| --- | --- | --- | --- | --- |
| TP0 | Inspection and instrument checks | None | None | 1 day |
| TP1 | Limit and fault response, cold | O4 | R10, R12 | 0.5 day |
| TP2 | Bake-out and commissioning | O4 | R13 | 3 days |
| TP3 | Charge | O1 | R3, R8 | 1 day |
| TP4 | Cool-down | O2 | R7 | 2 days |
| TP5 | Discharge | O3 | R4, R5 | 4 days |
| TP6 | Cycling | O5 | R19 | 5 weeks |

*Table 1. Test procedures, in order of execution.*

Procedure numbers follow the order in which the procedures are run. The limit test comes before any heating, and the charge test starts from the uniform 150 °C that the bake-out leaves behind. Sensor tags (T1 to T6) are those of TBK-PRC-002, section 3. They are not the same thing as the procedure numbers.

## 1. Test article and configuration

The article is built to TBK-DWG-002 Rev P1 and `bom/bom-test-article.csv`. Any departure from the drawing is recorded in the test log before TP0 and repeated in the report. The firmware version (Git commit) is recorded at the start of every procedure.

The firmware must provide five things before TP1:

1. **Charge mode:** full power until T1 reaches its setpoint, then PI control to hold it. The setpoint is adjustable, 550 °C by default.
2. **Hold mode:** PI control on T1 at a lower setpoint, used for the bake-out.
3. **Blower mode:** fixed PWM duty set from the Wi-Fi interface.
4. **Logging:** every channel, the SSR duty and the blower duty at 10 s intervals to a CSV file, with a monotonic time stamp.
5. **Safe state:** heaters off (SSR input low, with a pull-down resistor on the pin) after a reset, an open thermocouple on T1, a T1 reading above 575 °C or loss of the log for 60 s.

The firmware in `firmware/` provides all five, and `firmware/README.md` gives the wiring, commands and fault codes. It adds two further trips: T3 or T4 above 560 °C, and a stalled main loop. The logging host is `firmware/tools/logger.py`. Its polling is the log heartbeat in item 5, so stopping the logger is how TP1 step 5 tests that trigger. The T1 injection in TP1 step 5 uses the `esp32dev_test` build.

## 2. Instrumentation

| Tag | Quantity | Location | Sensor and reader |
| --- | --- | --- | --- |
| T1 | Well-wall temperature (control) | Well W1 at (90, 75) mm, outer face toward the drum wall, 300 mm above the drum floor | Type K, MI 3 mm, 500 mm; MAX6675 |
| T2 | Well-wall temperature (limit) | Well W3 at (−90, −75) mm, same height and face | Type K, MI 3 mm, 500 mm; REX-C100 |
| T3 | Sand temperature, center | Drum axis, 300 mm above the drum floor | Type K, MI 3 mm, 500 mm; MAX6675 |
| T4 | Sand temperature, outer | On the ray through W1, 151 mm from the axis (34 mm from the W1 center, 20 mm from the drum wall), 300 mm above the floor | Type K, MI 3 mm, 500 mm; MAX6675 |
| T5 | Exchanger outlet air | 50 mm inside the top of the outlet leg, on its axis | Type K kit probe; MAX6675 |
| T6 | Room and inlet air | 300 mm from the blower intake, shaded from the unit | Type K kit probe; MAX6675 |
| P | Heater power | Derived from SSR duty, line voltage and measured hot resistance | ESP32 log and multimeter |
| V | Exchanger airflow | Outlet leg top, before the stack is fitted | Bag method: 159 L (42 gal) contractor bag and stopwatch |
| C | Drum circumference | At 100 mm, 330 mm and 560 mm above the drum bottom, over the bare drum | Steel tape, 1 mm graduation |
| M | Sand mass | Every bag before filling | Bathroom scale, 0.1 kg graduation |

*Table 2. Instrumentation.*

The tips sit 300 mm above the drum floor, within the heated length (45 mm to 451 mm) and clear of both its ends. At that height the 500 mm probes end inside the top insulation, where their lead junctions stay cool. T3 and T4 sit at radii the model can reproduce. T4 is 34 mm from the center of W1, inside that heater's cell, and is compared with the model at 34 mm. T3 lies 117 mm from all four wells, beyond the 84 mm cell radius, and is compared with the model's outer edge. Before filling, photograph each thermocouple against a steel rule and record its as-built position to ±5 mm.

### 2.1 Checks before testing

- **Thermocouple channels.** Put all six probes in an ice bath (0 °C) and then in boiling water (100 °C less about 0.0033 K per meter of site elevation). Accept a channel if it reads within ±2 K at both points, and record its offsets. Correct the logged data with them.
- **Heater resistance.** Measure each heater cold with the multimeter; the expected value is 55 Ω to 60 Ω. Record the values and compute the four-in-parallel resistance.
- **Line voltage.** Measure it at the receptacle, under load, at the start and end of every heated procedure.
- **Airflow.** With the stack off and the unit cold, tape the bag mouth over the outlet leg top. Time the fill at blower duties of 25 %, 50 %, 75 % and 100 %, three times each. The result is the duty-to-airflow table used in TP5.

### 2.2 Measurement uncertainty

| Quantity | Uncertainty | Basis |
| --- | --- | --- |
| Temperature, 20 °C to 600 °C | ±5 K | Type K standard limits (±2.2 K or ±0.75 %) plus converter, after the two-point check |
| Heater power | ±5 % | Line voltage read twice per run; NiCr resistance rises about 4 % from cold to 600 °C and is corrected |
| Energy input | ±5 % | Integrated power |
| Exchanger airflow | ±10 % | Bag method, mean of three fills; hot running changes the system resistance |
| Exchanger duty | ±12 % | Airflow and temperature rise combined |
| Standby loss from cool-down | ±15 % | Slope of the estimated mean temperature; sand mass ±1 % |
| Drum circumference | ±1 mm in 1,080 mm (±0.1 %) | Steel tape, same person, same marks |

*Table 3. Measurement uncertainty.*

The mean sand temperature cannot be measured directly with three sand-side thermocouples. The analysis therefore does not estimate it from the sensors. Instead, the model is run with the measured heater power as its input, and its predicted T1, T3 and T4 are compared with the measurements (section 9).

## 3. Safety

The article runs at up to 550 °C inside, with 1.0 kW on a 120 V receptacle, and it releases hot air during discharge.

> **Safety:** Stop the test, press STOP and let the unit cool if any of the following occurs: T1 or T2 above 575 °C; smoke from the unit after TP2 is complete; a GFCI trip; any jacket surface above 45 °C; a smell of hot electrical insulation from the enclosure; or loss of logging for more than 60 s during heating.

> **Safety:** Do not leave the article unattended until TP1 has passed and the first charge (TP3) has run without incident. After that it may run unattended only with the latching limit in service, the smoke alarm in the room working, and 1 m clear of combustibles all round and above the stack.

> **Safety:** Wear a P100 or N95 respirator, gloves and eye protection when opening the insulation. Do not open the lid or pull a heater until T3 reads below 60 °C.

## 4. TP0 Inspection and instrument checks

1. Inspect the build against TBK-DWG-002. Record the sand mass per bag and the total (target 68 kg ± 1 kg) and the as-built thermocouple positions.
2. Mark the three circumference heights on the bare drum with a paint pen. Measure and record them before the insulation is fitted. These are the cycle-0 values for TP6.
3. Carry out the checks in section 2.1.
4. Confirm the receptacle is GFCI protected by pressing its TEST button, and that nothing else is on the circuit.

**Pass:** all channels within ±2 K; heater resistances within 55 Ω to 60 Ω and within 5 % of one another; sand mass 67 kg to 69 kg.

## 5. TP1 Limit and fault response, cold

The heaters stay cold throughout. T2 is withdrawn from its well only for this test and refitted afterward.

1. Set the REX-C100 to open its relay at 600 °C. Power the unit, press START, and confirm the latching relay pulls in. The heaters must not be energized, so hold the SSR input low from the firmware.
2. Place the T2 tip in the jet of a heat gun beside a reference Type K probe. Raise the temperature slowly, at about 5 K/s near 600 °C. Record the reading of each at the moment the relay drops.
3. Remove the heat. Confirm the relay stays open when T2 falls below 600 °C, and that it closes only when START is pressed.
4. Press STOP with the relay latched and confirm it drops. Unplug the cord, plug it back in, and confirm the relay stays open until START is pressed.
5. With the heaters enabled at a 10 % duty, check each firmware safe-state trigger: unplug T1 at its connector; force a T1 reading above 575 °C with a test build; reset the ESP32; stop the logging host. Record the time to heaters off for each.

**Pass:** the relay drops at 600 °C ± 10 K by the reference probe; it latches open in every case; each firmware trigger turns the heaters off within 10 s.

## 6. TP2 Bake-out and commissioning

This procedure dries the sand, burns off the stone wool binder and the drum's residues, and leaves the bed at a uniform 150 °C for TP3.

1. Check the insulation resistance of each heater, lead to sheath, with an insulation tester at 500 V. Borrow or rent the tester, since it is not in the BOM. If none is available, record the multimeter reading on its highest range and note the lower confidence. Expect low values if the MgO has absorbed moisture; the bake-out cures this.
2. Ventilate the room. Hold T1 at 200 °C in hold mode until T3 reaches 100 °C. Leave the U-tube legs open so steam can escape.
3. Raise the T1 setpoint to 300 °C. Hold until T3 and T4 are both within 10 K of 150 °C, then lower the T1 setpoint so that T1, T3 and T4 settle within 15 K of 150 °C for 6 h.
4. Note any smoke or odor and when it stopped.
5. Repeat step 1 on the hot unit with the power off.

Assumption: washed play sand arrives with 3 % to 5 % moisture. Driving off 2 kg to 3.4 kg of water takes 1.5 kWh to 2.5 kWh on top of heating the bed, so the bake-out takes about two days.

**Pass:** insulation resistance of 1 MΩ or more per heater at 500 V after the bake-out; no smoke in the last 12 h; T1, T3 and T4 within 15 K of 150 °C for 6 h.

## 7. TP3 Charge

1. Start from the end state of TP2. Tape the U-tube leg ends and switch off the blower.
2. Record the line voltage. Switch to charge mode with the T1 setpoint at 550 °C.
3. Log until T3 reaches 420 °C or 24 h have passed, whichever comes first. Record the line voltage every 4 h.
4. Note the time at which the SSR duty first falls below 100 %. The model predicts 2.1 h (TBK-CAL-002, section 3).

The unit is full, at a 450 °C mean, when the fitted model says so (section 9). The 420 °C T3 end point is a practical stop that the model predicts shortly before full charge.

**Pass:** the fitted model reproduces T1, T3 and T4 with an RMS error of 10 K or less; its controller-driven run predicts the time to 80 % charge within 10 % of the measured energy balance; and the heater power correction is within 5 % (section 9).

**Also report:** the unfitted prediction error; the fitted sand conductivity multiplier and contact conductance; and the time at which the well-wall limit was reached.

## 8. TP4 Cool-down

1. Immediately after TP3, switch the heaters off. Leave the blower off with the legs taped.
2. Log for 48 h. Once an hour for the first 6 h, and then every 12 h, record the jacket temperature at mid-height on four sides and on the top with a contact thermometer. Record room temperature from T6.
3. Remove the tape from the leg ends at the end of the test.

**Pass:** the measured loss at a 450 °C mean, from the fitted cooling rate, is within 20 % of the 249 W predicted by TBK-CAL-002 before fitting. No jacket surface exceeds 45 °C.

**Also report:** the fitted insulation conductivity multiplier; loss at 300 °C and 150 °C; any hot spot on the jacket.

## 9. Analysis method

The analysis script `docs/05-tests/tbk_tst_001_fit.py` fits four values to the TP3 and TP4 data:

- `k_sand`, a multiplier on the sand conductivity;
- `h_contact`, the wall contact conductance, in W/(m² K);
- `k_ins`, a multiplier on the stone wool and firebrick conductivity; and
- `p_scale`, a correction to the logged heater power, which carries the ±5 % uncertainty of Table 3.

The script drives the TBK-CAL-002 model with the measured heater power instead of the model's own controller. It then minimizes, by Levenberg–Marquardt least squares, the RMS difference between measured and modeled T1 (well wall), T4 (cell at 34 mm) and T3 (cell outer edge), over the whole TP3 and TP4 record at 60 s spacing. The model starts from a uniform bed at the mean of T3 and T4 in the first row.

**Why the four values can be separated:**
- The cool-down has no heater power, so it fixes `k_ins` on its own.
- With the loss known, the rate at which the bed heats in TP3 fixes `p_scale`.
- The shape of the charge curves at the three radii fixes `k_sand` and `h_contact`.

The script reports each value with a 95 % interval from the fit's Jacobian. That interval is optimistic, because successive residuals are correlated; treat it as a lower bound on the uncertainty.

The script reports these checks:

- **RMS error**, fitted and unfitted, overall and for each thermocouple.
- **Time to 80 % charge.** The measured value comes from the energy balance: the corrected heater energy less the loss fitted on the cool-down, added to the heat at the start. The predicted value comes from a run of the fitted model under its own 550 °C well-wall controller. Agreement shows that the real controller and bed take heat as fast as the model says.
- **Energy closure over TP3.** The corrected heater energy is compared with the stored heat plus the fitted loss. The stored heat is estimated from the measured temperatures alone, through a linear radial profile between T1, T4 and T3. The estimate reads slightly high because T1 includes the contact drop at the well wall. Closure within 10 % is expected.
- **Standby loss** from the fitted envelope, at 450 °C, 300 °C and 150 °C, against the 249 W prediction.
- **Power correction** within 5 %. A larger correction points to a wrong `v_line` or `r_heat` setting in the firmware.

TP5 is then predicted with the fitted values and no further fitting. Its only comparison is between measured and modeled exchanger duty, averaged over each hour. The first hour is not scored, because the model starts from a uniform bed.

The commands are as follows, run from the repo root:

```bash
python docs/05-tests/tbk_tst_001_fit.py selftest
```

```bash
python docs/05-tests/tbk_tst_001_fit.py fit --tp3 docs/05-tests/data/DATE_TP3.csv --tp4 docs/05-tests/data/DATE_TP4.csv
```

```bash
python docs/05-tests/tbk_tst_001_fit.py tp5 --tp5 docs/05-tests/data/DATE_TP5.csv
```

Results are written as JSON and SVG to `docs/05-tests/results/`. The self-test builds charge, cool-down and discharge records from known values with the model. It adds 1.5 K of thermocouple noise, a 2 % power error and 3 % duty noise, then fits them. It passes only if every value is recovered: `k_sand` and `k_ins` within 5 %, `h_contact` within 30 %, `p_scale` within 2 %, and TP5 within 15 %. The TP5 part checks the plumbing of the prediction, not the physics, because the same model made the data.

## 10. TP5 Discharge

1. Charge to full as in TP3, allowing up to 16 h.
2. Remove the tape, fit the blower and set it to the duty that gives 1.0 L/s from the section 2.1 table. Fit the stack.
3. Run at constant blower duty for 8 h, then 2.0 L/s for 8 h, then 4.0 L/s until T3 falls to 180 °C.
4. Recharge to full and repeat with a closed-loop demand of 250 W. The firmware adjusts the blower duty to hold ṁ cp (T5 − T6) at 250 W, using the airflow table.

Exchanger duty is ṁ cp (T5 − T6), with ṁ from the airflow table and cp of air at the mean of T5 and T6.

**Pass:** at each constant-airflow step, measured duty averaged over each hour is within 15 % of the model's prediction using the parameters fitted in section 9. In the closed-loop run, 250 W is held for 8.8 h ± 1.5 h.

**Also report:** the peak T5; the stack exit temperature measured with the contact thermometer; and whether the blower met 4.0 L/s hot.

## 11. TP6 Cycling

1. Run 25 cycles. Each cycle is a charge to full as in TP3, followed by a discharge at 4.0 L/s until T3 falls to 180 °C. This takes about 32 h per cycle.
2. Every five cycles, when T3 is below 60 °C, open the side insulation at the three marks. Measure the drum circumference at each and refit the insulation. Photograph the drum and the bricks.
3. Log continuously. Note any drift in the time for T1 to reach 550 °C from cycle to cycle; a steady increase suggests the sand is packing or breaking down around the wells.
4. After cycle 25, open the lid and inspect the sand surface. Draw one heater, and inspect it and its well.

**Pass:** circumference growth under 0.25 % at every height after 25 cycles, with no trend that would exceed 1 % in 1,000 cycles when extrapolated (full-scale R19); no crushing of the firebricks; heaters within 5 % of their TP0 resistance.

## 12. Schedule and records

| Week | Procedures |
| --- | --- |
| 1 | TP0, TP1, TP2 |
| 2 | TP3, TP4, TP5, analysis of TP3 and TP4 |
| 3 to 7 | TP6 (25 cycles of about 32 h) |

*Table 4. Schedule.*

Raw logs are saved as `docs/05-tests/data/YYYY-MM-DD_TPn.csv`. Record in the file header the firmware commit, the channel offsets from section 2.1 and the line voltage readings. Photographs and daily notes go in `build-log/` as dated entries. Nothing in the raw data is edited; corrections are applied in the analysis script and recorded there.

The results, fitted parameters and pass or fail for every procedure go in test report TBK-TST-002. After running the analysis, `python docs/05-tests/tbk_tst_002_fill.py` fills the report's TP3 to TP5 results, its fitted-property tables and a re-run of the full-scale sizing with the fitted values; the rest is written by hand from the build log and test records. The fitted values are then entered in `tbk_cal_001.py`, and TBK-CAL-001 is reissued. That reissue decides the options for the full-scale charge-time gap (TBK-PRC-001, section 8).

## 13. Prerequisites

- [ ] Test article built and inspected to TBK-DWG-002 (TP0).
- [x] Firmware with the five functions in section 1, committed to `firmware/`; host unit tests pass.
- [ ] Firmware flashed and the wiring checked against `firmware/README.md`, Table 1.
- [x] Analysis script `docs/05-tests/tbk_tst_001_fit.py`, checked against a synthetic data set made with `tbk_cal_002.py` (`selftest` passes).
- [ ] Insulation tester borrowed or rented for TP2.
- [ ] Contact thermometer for jacket and stack surfaces (a Type K bead probe on a spare MAX6675 channel is acceptable).
- [ ] Smoke alarm working in the test room.
