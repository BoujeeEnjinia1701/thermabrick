---
doc_id: TBK-TST-002
title: ThermaBrick test article test report
project: ThermaBrick
doc_type: Test report
version: "0.1"
status: Draft
date: '2026-09-24'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-24'
  author: Amish Chadha
  change: Template. Structure follows TBK-TST-001; sections 5, 6 and 8 and the summary rows for TP3 to TP5 are filled from the analysis results by tbk_tst_002_fill.py
---

# ThermaBrick test article test report

*Summary to be written once the tests are complete. State in two or three sentences whether the test article met TBK-TST-001, give the measured sand conductivity, contact conductance and insulation conductivity against the values assumed in TBK-CAL-001, and say what they mean for the full-scale charge-time requirement R3 (section 8).*

| Procedure | Dates | Pass criterion (TBK-TST-001) | Result | Pass |
| --- | --- | --- | --- | --- |
| TP0 Inspection and instrument checks | | Channels within ±2 K at 0 °C and 100 °C | | |
| TP1 Limit and fault response | | Trip at 600 °C ± 10 K; latches; firmware safe state within 10 s | | |
| TP2 Bake-out and commissioning | | 1 MΩ or more per heater at 500 V; no smoke in the last 12 h | | |
<!-- auto:summary -->
| TP3 Charge | | Fitted RMS 10 K or less; time to 80 % within 10 %; power correction within 5 % | *filled by script* | |
| TP4 Cool-down | | Loss at 450 °C within 20 % of 249 W before fitting | *filled by script* | |
| TP5 Discharge | | Hourly duty within 15 % of the model, no refit | *filled by script* | |
<!-- /auto:summary -->
| TP6 Cycling | | Circumference growth under 0.25 % after 25 cycles | | |

*Table 1. Results against TBK-TST-001. The TP3 to TP5 rows are filled by `tbk_tst_002_fill.py`; enter the dates by hand.*

## 1. Test article as built

The test article was built to TBK-PRC-002 and `docs/07-build/test-article-build.md`, with the deviations in Table 2. Each deviation comes from the build log, and each should have its document change committed before this report is released.

| Deviation | Build log entry | Effect on the tests | Document changed |
| --- | --- | --- | --- |
| *None recorded yet* | | | |

*Table 2. Deviations from the design.*

| Item | Value |
| --- | --- |
| Sand mass and depth | kg, mm (build stage F) |
| Heater cold resistances H1 to H4 | Ω |
| Firmware commit | |
| Analysis script commit | |
| Parts cost, actual against the $727.70 BOM | $ |

*Table 3. As-built record.*

## 2. Instrumentation and calibration (TP0)

| Channel | Reading at 0 °C | Reading at 100 °C (corrected for elevation) | Offset applied |
| --- | --- | --- | --- |
| T1 | | | |
| T2 (REX-C100) | | | |
| T3 | | | |
| T4 | | | |
| T5 | | | |
| T6 | | | |

*Table 4. Thermocouple checks.*

| Blower duty | Airflow, mean of three fills (L/s) |
| --- | --- |
| 25 % | |
| 50 % | |
| 75 % | |
| 100 % | |

*Table 5. Airflow calibration, as loaded into the firmware with `/config?air=`.*

## 3. TP1: Limit and fault response

| Trigger | Expected | Measured | Pass |
| --- | --- | --- | --- |
| REX-C100 trip on T2 (reference probe reading) | 600 °C ± 10 K | | |
| Latch holds after T2 cools | Stays open until START | | |
| STOP with K1 latched | Drops | | |
| Power loss and return | Stays open until START | | |
| T1 unplugged | Heaters off within 10 s | | |
| T1 above 575 °C (test build) | Heaters off within 10 s | | |
| ESP32 reset | Heaters off within 10 s | | |
| Logging host stopped | Heaters off within 70 s | | |

*Table 6. Limit and fault results.*

## 4. TP2: Bake-out and commissioning

| Heater | Insulation resistance before (MΩ at 500 V) | After (MΩ at 500 V) |
| --- | --- | --- |
| H1 | | |
| H2 | | |
| H3 | | |
| H4 | | |

*Table 7. Heater insulation resistance.*

*Record when smoke and odor stopped, the time taken to settle at 150 °C, and any condensation or steam at the leg openings.*

## 5. TP3 and TP4: Fitted properties

<!-- auto:fit -->
*Filled by `tbk_tst_002_fill.py` from `results/tbk_tst_001_fit.json`.*
<!-- /auto:fit -->

## 6. TP5: Discharge prediction

<!-- auto:tp5 -->
*Filled by `tbk_tst_002_fill.py` from `results/tbk_tst_001_tp5.json`.*
<!-- /auto:tp5 -->

*Record the peak T5, the stack exit temperature from the contact thermometer, and whether the blower reached 4.0 L/s hot.*

## 7. TP6: Cycling

| Cycle | Circumference at 100 mm (mm) | At 330 mm (mm) | At 560 mm (mm) | Time for T1 to reach 550 °C (h) |
| --- | --- | --- | --- | --- |
| 0 | | | | |
| 5 | | | | |
| 10 | | | | |
| 15 | | | | |
| 20 | | | | |
| 25 | | | | |

*Table 8. Drum circumference and charge behavior over 25 cycles.*

*State the growth at each height after 25 cycles, the trend extrapolated to 1,000 cycles (full-scale R19), the brick condition, and the heater resistances after cycling.*

## 8. Implications for the full-scale design

<!-- auto:fullscale -->
*Filled by `tbk_tst_002_fill.py`: TBK-CAL-001 re-run with the fitted values.*
<!-- /auto:fullscale -->

*State whether TBK-CAL-001 should be reissued with the fitted values, and which option in TBK-PRC-001, section 8 (charge time), the results support.*

## 9. Anomalies and observations

*List anything unexpected, with the build log entry and data file where it is recorded.*

## 10. Conclusions and recommendations

*Numbered conclusions, each traced to a table or figure above, then the recommended next steps.*

## Appendix A. Data files

| Procedure | File | Firmware |
| --- | --- | --- |
| | `docs/05-tests/data/` | |

*Table 9. Raw data files. These are never edited; corrections are applied in the analysis script.*
