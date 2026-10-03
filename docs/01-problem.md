---
doc_id: TBK-PRB-001
title: ThermaBrick problem statement
project: ThermaBrick
doc_type: Problem statement
version: "0.11"
status: Draft
date: '2026-10-02'
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
  change: Developed the energy case, users and context, constraints, success measures and scope; flagged the budget gap found in the v0.2 costing
- version: "0.3"
  date: '2026-09-24'
  author: Amish Chadha
  change: Recorded the budget decision to build a reduced-scale test article within $600 first
- version: "0.4"
  date: '2026-09-24'
  author: Amish Chadha
  change: Noted that the test article estimate is now $635.70 after the enclosure fit check; the way back to $600 is open
- version: "0.5"
  date: '2026-09-24'
  author: Amish Chadha
  change: Recorded the decision to accept the test article at $635.70
- version: "0.6"
  date: '2026-09-24'
  author: Amish Chadha
  change: Test article budget raised to $727.70 for the parts the build procedure found
- version: "0.7"
  date: '2026-09-24'
  author: Amish Chadha
  change: 'Review pass: the $727.70 budget returned to proposed, awaiting Amish; only $635.70 was accepted by Amish'
- version: "0.8"
  date: '2026-09-25'
  author: Amish Chadha
  change: Recommendations accepted by Amish (DDR-002)
- version: "0.9"
  date: '2026-10-01'
  author: Amish Chadha
  change: 'Operating mass 415 kg and full-scale estimate $3,854 after the design was made constructable (TBK-DDR-003); budget worded as a value-engineering target'
- version: "0.10"
  date: '2026-10-02'
  author: Amish Chadha
  change: 'Standby loss open decision recorded as decided on 2026-10-02 (TBK-DEC-001)'
- version: "0.11"
  date: '2026-10-02'
  author: Amish Chadha
  change: 'Full-scale estimate $3,869 after the warning labels line (BOM line 47)'
---

# ThermaBrick problem statement

Homes with rooftop solar increasingly export their midday surplus for a few cents per kilowatt-hour, or lose it to curtailment. The same homes then buy gas or grid power at full price to heat the evening. ThermaBrick stores that surplus as heat in sand at up to 450 °C and releases it as warm air when the house needs it. It aims to shift about 18 kWh(th) a day from midday to the evening and night, using parts that a capable maker can buy and assemble in a garage.

## 1. The energy case

The mismatch is one of timing, not quantity. A 6 kWp rooftop array in a sunny, cold climate such as Denver produces roughly 20 to 25 kWh on a clear January day, most of it between 10:00 and 15:00. Household base load over those hours is typically 0.5 to 1.5 kW. That leaves roughly 8 to 14 kWh of midday surplus on a sunny winter day, and more in spring and autumn. Heating demand peaks between 17:00 and 08:00, after the surplus has gone.

Assumptions:

- Array yield of 3.5 to 4.2 kWh per kWp on a clear January day at 40° N.
- Heating demand of 20 to 60 kWh(th) per day for a small, reasonably insulated house or a large room.

Some tariffs and installations pay little or nothing for exports. Examples include the California net billing tariff that replaced net metering in 2023, export-capped installations and zero-export inverters. There, the surplus is worth far more as heat than as export. At an export value of $0.05/kWh, 18 kWh of surplus earns $0.90. The same 18 kWh(th) of heat displaces about 0.68 therm of gas at 90 % furnace efficiency, or 18 kWh of resistance heating bought at the retail rate.

A battery can also shift the surplus, but stationary lithium storage costs several hundred dollars per kilowatt-hour of capacity. Its cycles are better spent on loads that need electricity. Heat is the one large household load that can be stored cheaply in an inert, abundant material. Sand is nearly free, does not burn and does not degrade with cycling.

The honest limit of the case is scale. At this size standby losses are high (TBK-CAL-001, section 5), and the parts cost equals several years of savings. The prototype is a technology demonstrator and a design reference. It is not an economic product, and payback is not a design goal.

## 2. Users and context

The primary user is a homeowner or experienced maker who:

- has rooftop PV of 4 kWp or more and a way to read grid export in real time, such as an inverter API or an energy meter;
- has a slab-on-grade space inside the heated envelope, such as a basement, an attached garage workshop or a ground-floor utility room, with 1.5 m by 1.5 m of floor space;
- can have a dedicated 240 V, 20 A circuit installed; and
- is comfortable with pipe threading, sheet metal and low-voltage electronics, and will hire an electrician for the branch circuit where local code requires it.

The secondary audience is other designers, students and community energy groups, who will use the documentation to adapt the design. For them the calculation note and the parametric model matter as much as the hardware.

The operating context sets the design. The unit charges from about 10:00 to 16:00 whenever export is detected, holds heat through the late afternoon, and releases it through a room register from evening to morning. In the heating season its standby loss warms the same room. That heat is not wasted, but it cannot be switched off. Outside the heating season the unit is idle.

## 3. Constraints

- **Garage-buildable.** No welding, no pressure vessel and no custom machining. Cutting and threading pipe, riveting sheet metal and basic electrical assembly are acceptable.
- **Safe at the temperatures involved.** Independent hardware over-temperature protection, no coated or galvanized steel in hot zones, cool touchable surfaces and insulation fibers that are safe to handle.
- **Standard supply.** 240 V split phase on one 20 A circuit, the normal North American arrangement for a fixed heater.
- **Indoor siting on a concrete slab.** The unit weighs about 415 kg in service.
- **Prototype budget of about $600 USD.** The v0.2 costing (`bom/bom.csv`) estimated $3,674 for the full-scale design; the constructable design (TBK-DDR-003) is estimated at $3,869, USD 3,141 over the USD 728 value-engineering target. The target is a hypothetical control figure for value engineering, not a spending limit. The budget now funds a reduced-scale test article, with a budget of $727.70 decided by Amish on 2026-09-25 (TBK-DDR-002). The test article is archived and on hold with TRL 4 (section 5).

## 4. What success looks like

The v0.2 draft sets the following measures, which TBK-REQ-001 turns into verifiable requirements. ThermaBrick:

- stores at least 18 kWh(th) between 150 °C and 450 °C sand mean temperature;
- absorbs at least 11 kWh in 4 h of full surplus and fills in 8 h or less;
- delivers a steady 1.0 kW of warm air through most of the stored range, with supply air at 55 °C or below;
- never lets any sand pass 550 °C, and keeps every accessible surface at 45 °C or below;
- follows live PV export, so it draws surplus power and never imports from the grid to charge; and
- can be reproduced entirely from the published model, drawings, BOM and firmware.

## 5. Open decisions

1. **Budget.** Decided by Amish on 2026-09-24. The $600 budget funds a reduced-scale test article first: a 16 US gal drum storing about 6 kWh(th), built with the same heater cells as the full-scale design (TBK-PRC-002). Its measurements will settle sand conductivity, contact conductance and standby loss. The full-scale budget will be revisited with those results. After the controller enclosure was modeled, the test article estimate rose to $635.70. Decided 2026-09-24: accept $635.70 as the test article budget, with every part specified, rather than defer parts or rely on parts on hand. The build procedure then found $92.00 of parts the BOM had missed (insulation, cable, wiring consumables and thermocouple extension); Amish had them added to the BOM, which now totals $727.70. Decided by Amish, 2026-09-25: go with recommendation. The test article budget is raised from $635.70 to $727.70 (TBK-DDR-002). The test article is archived under `archive/out-of-phase-trl4/` and is on hold with TRL 4, so nothing will be bought until TRL 4 resumes. Revisiting the full-scale budget with the test article's results is also decided, and on hold for the same reason.
2. **Standby loss.** Decided by Amish on 2026-10-02 (TBK-DEC-001): 459 W of uncontrolled output at full charge is accepted for now; the loss-reduction options in TBK-CAL-001, Table 5 are decided together with the R3 charge-time fix once the test article has measured loss.

## 6. Out of scope

- Domestic hot water. A later revision could add a water coil to the collector.
- Charging from cheap night-rate grid power. The controller could do it, but it is not a design driver.
- Certification to UL 2021 or a similar appliance standard. The prototype is a documented experimental build, not a listed product.
- Multi-unit or district scale.
