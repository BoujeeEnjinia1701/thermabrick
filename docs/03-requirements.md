---
doc_id: TBK-REQ-001
title: ThermaBrick requirements
project: ThermaBrick
doc_type: Requirements
version: "0.8"
status: Draft
date: '2026-09-24'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-24'
  author: Amish Chadha
  change: Initial scaffold
- version: "0.2"
  date: '2026-09-24'
  author: Amish Chadha
  change: Defined 20 requirements with targets, verification methods and v0.2 compliance status traced to TBK-CAL-001
- version: "0.3"
  date: '2026-09-24'
  author: Amish Chadha
  change: Updated R3, R4 and R5 status for standby loss (TBK-CAL-001 v0.2), so R3 is now not met; R20 notes the $600 reduced-scale test article
- version: "0.4"
  date: '2026-09-24'
  author: Amish Chadha
  change: R20 test article estimate updated to $599.70 after adding the pull-down resistors
- version: "0.5"
  date: '2026-09-24'
  author: Amish Chadha
  change: R20 test article estimate updated to $635.70 after the controller enclosure fit check (TBK-DWG-005)
- version: "0.6"
  date: '2026-09-24'
  author: Amish Chadha
  change: R20 records the decision to accept the test article at $635.70
- version: "0.7"
  date: '2026-09-24'
  author: Amish Chadha
  change: R20 test article budget updated to $727.70 after the build procedure's additions
- version: "0.8"
  date: '2026-09-24'
  author: Amish Chadha
  change: 'Review pass: R20 shows $727.70 as the BOM total, proposed and awaiting Amish; the accepted budget remains $635.70'
---

# ThermaBrick requirements

The v0.2 design meets 15 of the 20 requirements below, by analysis or by design. Three depend on firmware or on testing that has not yet been done (R12, R18 and R19). Two are not met. Charge time (R3) misses by 1.6 h once standby loss is counted. Cost (R20) is about six times the target; the $600 budget now funds a reduced-scale test article instead (TBK-PRB-001, section 5). Every requirement will be confirmed by test on the first build.

Verification methods are analysis (A), inspection (I), demonstration (D) and test (T). Status reflects the v0.2 analysis in TBK-CAL-001 and the BOM. "Met (A)" means shown by analysis and not yet tested.

## 1. Performance

| ID | Requirement | Target | Verification | v0.2 status |
| --- | --- | --- | --- | --- |
| R1 | Stored heat between 150 °C and 450 °C energy-weighted mean sand temperature | 18 kWh(th) or more | A: TBK-CAL-001 section 2. T: calorimetric discharge (air flow and temperature rise) | Met (A): 18.3 kWh(th) |
| R2 | Charge power drawn only from PV surplus, following export in real time | 0 to 3.0 kW in steps of 25 W or finer; grid import from charging 50 Wh per day or less | D: log export meter and heater power through three sunny days | Met by design |
| R3 | Charge acceptance from empty with full surplus available | 11 kWh or more in 4 h; full in 8 h or less | A: TBK-CAL-001 section 3. T: charge from 150 °C at 3.0 kW | **Not met (A):** 10.9 kWh in 4 h, full in 9.6 h |
| R4 | Rated heat output | 1.0 kW held down to 170 °C sand mean or lower | A: TBK-CAL-001 section 4. T: discharge at 1.0 kW demand | Met (A): held 14.3 h, to 154 °C |
| R5 | Boost heat output | 1.5 kW for 8 h or more from full | A: TBK-CAL-001 section 4. T | Met (A): 8.1 h |
| R6 | Supply air temperature at the register | 55 °C or below at all times | T: log supply air through charge and discharge | Met by design (50 °C setpoint) |
| R7 | Standby loss | 500 W or less at full charge; 9 kWh or less over 24 h idle from full | A: TBK-CAL-001 section 5. T: 24 h cool-down from full | Met (A): 459 W; 8.7 kWh |

## 2. Safety

| ID | Requirement | Target | Verification | v0.2 status |
| --- | --- | --- | --- | --- |
| R8 | Peak temperatures | Sand and well wall 550 °C or below; heater sheath 700 °C or below; drum wall 500 °C or below | A: TBK-CAL-001 section 3. T: well-wall and sand thermocouples, plus a temporary drum-wall thermocouple beside a ring B well | Met (A): 550 °C, 634 °C and about 480 °C |
| R9 | Accessible surface temperature at full charge, 20 °C room | 45 °C or below on the jacket; hot outlet duct guarded | A: TBK-CAL-001 section 5. T: surface survey with a contact probe | Met (A): 26 °C side |
| R10 | Independent over-temperature protection | Hardware limit, separate from the ESP32, opens a 2-pole contactor at 600 °C well-wall temperature and latches until manually reset | I: wiring against the schematic. T: trip test with a heated thermocouple | Met by design |
| R11 | Electrical supply and protection | Dedicated 240 V, 20 A circuit with 2-pole GFCI protection; continuous current 16 A or less; supplementary fuses per heater group | A: TBK-CAL-001 section 6. I | Met (A): 12.5 A |
| R12 | Fail-safe behavior | On controller reset, loss of Wi-Fi, a sensor fault or a fan fault: heaters off, inlet damper closed | D: fault injection for each case | Firmware to be written |
| R13 | Materials in hot zones | No zinc, paint, liner or plastic above 200 °C; AES (body-soluble) fiber in place of refractory ceramic fiber | I: against the BOM | Met by design |

## 3. Physical and installation

| ID | Requirement | Target | Verification | v0.2 status |
| --- | --- | --- | --- | --- |
| R14 | Envelope | 1,250 mm diameter or less; 1,500 mm high or less, including ducts | I: CAD and as-built | Met: 1,209 mm by 1,462 mm |
| R15 | Siting and floor load | Indoors, inside the heated space, on a concrete slab; 450 kg or less in service | A: TBK-CAL-001 section 7 | Met (A): 410 kg |
| R16 | Buildability | No welding, machining or pressure parts; hand tools, a pipe threader and pop rivets only | I: build log | Met by design |
| R17 | Serviceability | Any heater replaceable from the top without removing sand | D: replace one heater | Met by design: heaters sit in wells |

## 4. Controls, openness and cost

| ID | Requirement | Target | Verification | v0.2 status |
| --- | --- | --- | --- | --- |
| R18 | Monitoring | Log all temperatures, heater power and export at 10 s intervals; report state of charge within 10 % of the calorimetric value | T: compare against R1 test | Firmware to be written |
| R19 | Durability | 1,000 charge cycles without drum growth over 1 % in circumference or loss of heater function | T: measure drum circumference every 25 cycles | Open: sand ratcheting risk, see TBK-PRC-001 section 8 |
| R20 | Prototype cost | About $600 USD in parts | I: against the BOM | **Not met:** $3,674 estimated for full scale. The reduced-scale test article (TBK-PRC-002) BOM totals $727.70. Amish accepted $635.70 on 2026-09-24; the rise to $727.70 is proposed, awaiting Amish (TBK-PRB-001, section 5) |

## 5. Traceability

The requirements trace to TBK-PRB-001 as follows: R1 to R7 to section 4 (success measures); R8 to R13 to section 3 (safety constraint); R14 to R17 to section 3 (buildability and siting); R18 to section 4 (reproducibility); R20 to section 3 (budget). R19 comes from the ratcheting risk identified in the design precis.
