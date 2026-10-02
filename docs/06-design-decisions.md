---
doc_id: TBK-DEC-001
title: ThermaBrick design decisions register
project: ThermaBrick
doc_type: Design decisions register
version: "0.1"
status: Draft
date: '2026-10-01'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
  - version: "0.1"
    date: '2026-10-01'
    author: Amish Chadha
    change: Register opened with the open decisions from REVIEW.md, TBK-PRC-001, TBK-DDR-002 and TBK-DDR-003; budget treated as a value-engineering target
---

# ThermaBrick design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/` or in the review note; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

| # | Decision needed | Options | Recommendation | Affects in the build | Source |
| --- | --- | --- | --- | --- | --- |
| 1 | Review the design-for-construction changes P1 to P11 | Accept them; ask for changes to any | Accept: each keeps what the unit does and the safety case | The whole build plan | TBK-DDR-003, Table 1 |
| 2 | Warning labels for hot surfaces and 240 V | (a) add one BOM line, about USD 15; (b) leave to the installer | (a) | Labels on the jacket, outlet guard, junction box and enclosure | TBK-DDR-003, C1; REVIEW 2026-09-26, item 4 |
| 3 | Air path layout beyond the unit (duct route, tee, fan, control enclosure on the wall) | (a) keep the plan's layout illustrative, with its siting rules; (b) add an installation layout sheet | (a) at TRL 3 | Build plan step 20 | TBK-DDR-003, C2; REVIEW 2026-09-26, item 2 |
| 4 | Standby loss: accept 459 W at full charge (8.7 kWh, 47 % of the window, per day idle) | (a) accept; (b) stainless upper inlet legs and a microporous hot face, 357 W for about USD 450 | None made | Inlet legs and the hot face of the insulation | TBK-PRC-001, section 9; TBK-CAL-001, Table 5 |
| 5 | Ground-fault protection | (a) 5 mA GFCI breaker; (b) 30 mA equipment ground-fault protection if MgO heaters trip a 5 mA device | Choose with the installing electrician | Main panel breaker (BOM line 39) | TBK-PRC-001, sections 8 and 9 |
| 6 | Renders: the 80 degree cut sector | Keep it for the hero and detail renders only; drawings and STEP stay whole | Keep for those renders | None; appearance only | REVIEW 2026-09-26, item 1 |
| 7 | Renders: fan, guard sleeve, intake and grille sizes | Accept as placeholders until the fan is chosen | Accept as placeholders | None; appearance only | REVIEW 2026-09-26, item 3 |
| 8 | Renders: cosmetic trim ring and kick plinth | Optional cosmetic parts, no BOM line | Treat as optional | None | REVIEW 2026-09-26, item 4 |
| 9 | Renders: insulation split into AES hot face and stone wool | Keep the split | Keep | None; no dimension changes | REVIEW 2026-09-26, item 5 |

## To confirm when parts are bought

| # | What to confirm | Why it matters | Source |
| --- | --- | --- | --- |
| 1 | The cartridge heaters can be made with 72 in (1,829 mm) ceramic-beaded leads | Shorter leads do not reach the junction box from the far wells | TBK-DDR-003, P9 |
| 2 | The 1-1/4 in elbows' centre-to-end size (about 44.5 mm) and thread make-up, with the 4 in nipple, give 155 mm between leg centres | Sets the U-tube leg spacing that matches the lid holes | TBK-DDR-003, P2 |
| 3 | The stone wool base board is rated 60 kPa or more at 10 % strain | It carries the firebrick load of 15.0 kPa with a safety factor of 4 | TBK-CAL-001, section 7 |
| 4 | The inline fan's pressure curve and speed input meet 60 L/s at 150 Pa | Sets the discharge air flow | TBK-PRC-001, section 9 |
| 5 | The drum's lid is 16 ga, its rim 597 mm and its bottom rim stands on a flat ring | The lid layout and the AES disc size depend on it | TBK-DDR-003, P3 and P5 |
| 6 | At the first firing (TRL 4): the galvanized jacket cap at the edge of the outlet hole stays below 200 °C | R13; if not, fit a listed double-wall stovepipe thimble | TBK-DDR-003, P8 |

## Value engineering

Value-engineering target: USD 728 (a hypothetical control target, not a limit; `budget_usd` in `project.yaml`, set as the reduced-scale test article budget by Amish on 2026-09-25). Estimated cost of the constructable full-scale design: USD 3,854 (USD 3,126 over the target). Main cost drivers and savings worth trying:

- The largest groups are insulation (USD 871), controls and instrumentation (USD 863), heaters and wells (USD 776) and the discharge exchanger and air path (USD 740). The largest single lines are the twelve cartridge heaters (USD 588), the stone wool batts (USD 225), the four stone wool boards (USD 180) and the eight thermocouples (USD 208).
- Making the design constructable added USD 180: longer heater leads and thermocouples, 4 in nipples, two firebricks, a second AES rope, fasteners, and the template, trim ring, guide rods and grommets.
- Savings worth trying (`bom/bom-notes.md`, Table 2): generic import heaters (about USD 300), a reconditioned drum (about USD 100), reading export from the inverter instead of a meter (USD 90), MAX31855 amplifiers (about USD 50), and an existing 240 V circuit (up to USD 190). with stone wool batts in place of board in the base (about USD 100), together about USD 830, which would bring the estimate to about USD 3,000, still far over the target; only the reduced-scale test article (archived, on hold with TRL 4) comes near it.

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-24 | Build a reduced-scale test article first, within the prototype budget | Amish | TBK-PRB-001, section 5 |
| 2026-09-25 | Test article budget USD 727.70; revisit the full-scale budget with its results (both on hold with TRL 4) | Amish: "i accept all your recommendations, go with them across all repos." | [TBK-DDR-002](decisions/0002-recommendations-accepted.md), A1, A2 |
| 2026-09-25 | Design decisions D1 to D8: silica sand 150 to 450 °C, cartridge heaters in capped wells, twelve 250 W wells, closed U-tubes, cold-side damper with mixing tee and heat trap, wells end at the lid, AES hot face with stone wool, 240 V burst-fire SSRs with contactor | Amish, same instruction | [TBK-DDR-002](decisions/0002-recommendations-accepted.md), A3 |
| 2026-09-25 | Requirement targets R1 to R20 as written, including the 500 °C drum-wall limit | Amish, same instruction | [TBK-DDR-002](decisions/0002-recommendations-accepted.md), A4, A5 |
| 2026-09-25 | R3 charge-time miss: choose the fix after the test article measures sand conductivity (on hold with TRL 4) | Amish, same instruction | [TBK-DDR-002](decisions/0002-recommendations-accepted.md), A6 |
| 2026-09-25 | Controller board stays deferred; KiCad install on hold with TRL 4 | Amish, same instruction | [TBK-DDR-002](decisions/0002-recommendations-accepted.md) |
| 2026-09-30 | The design is made physically buildable as the build plan is drawn | Amish: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." | [TBK-DDR-003](decisions/0003-design-for-construction.md) (its changes open for review, decision 1 above) |
| 2026-09-30 | Outstanding decisions live in this register, not in the build plan | Amish: "don't log outstanding decisions in this build plan - that is not the place for it." | This register |
| 2026-10-01 | Budgets are value-engineering targets, not limits | Amish: "the budgets are a hypothethical control target to ensure we are thinking along a value engineering lens." | This register, Value engineering |
