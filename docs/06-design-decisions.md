---
doc_id: TBK-DEC-001
title: ThermaBrick design decisions register
project: ThermaBrick
doc_type: Design decisions register
version: "0.4"
status: Draft
date: '2026-10-03'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
  - version: "0.1"
    date: '2026-10-01'
    author: Amish Chadha
    change: Register opened with the open decisions from REVIEW.md, TBK-PRC-001, TBK-DDR-002 and TBK-DDR-003; budget treated as a value-engineering target
  - version: "0.2"
    date: '2026-10-02'
    author: Amish Chadha
    change: 'Amish approved the recommendations for all nine open decisions on 2026-10-02 (TBK-DDR-003 accepted); moved to decisions made'
  - version: "0.3"
    date: '2026-10-02'
    author: Amish Chadha
    change: 'Cost restated to USD 3,869 with the warning labels (BOM line 47) and the approved wording; stray full stop fixed'
  - version: "0.4"
    date: '2026-10-03'
    author: Amish Chadha
    change: "Amish accepted the cost overrun against the value-engineering target on 2026-10-03; row added to decisions made; value engineering section updated"
---

# ThermaBrick design decisions register

Every design decision still to be made, and every decision made, in one place. Each decision is argued in full in its decision record under `docs/decisions/` or in the review note; this register is the index Amish works from. The build plan (`docs/05-build-plan.md`) describes the design as it stands and does not list open decisions.

## Open decisions

None. All open decisions were decided on 2026-10-02.

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

Value-engineering target: USD 728 (a hypothetical control target, not a limit; `budget_usd` in `project.yaml`, set as the reduced-scale test article budget by Amish on 2026-09-25). Estimated cost of the constructable design: USD 3,869 (USD 3,141 over the target). Main cost drivers and savings worth trying:

Amish accepted this overrun on 2026-10-03: the full-scale estimate of USD 3,869 against the USD 728 target (USD 3,141 over). Amish: "Cost over target - i accept all the cost variations and overruns". It stays reported against the target as an accepted overrun, and the savings below remain worth trying.

- The largest groups are insulation (USD 871), controls and instrumentation (USD 863), heaters and wells (USD 776) and the discharge exchanger and air path (USD 740). The largest single lines are the twelve cartridge heaters (USD 588), the stone wool batts (USD 225), the four stone wool boards (USD 180) and the eight thermocouples (USD 208).
- Making the design constructable added USD 180, and the approved warning labels USD 15: longer heater leads and thermocouples, 4 in nipples, two firebricks, a second AES rope, fasteners, and the template, trim ring, guide rods and grommets.
- Savings worth trying (`bom/bom-notes.md`, Table 2): generic import heaters (about USD 300), a reconditioned drum (about USD 100), reading export from the inverter instead of a meter (USD 90), MAX31855 amplifiers (about USD 50), and an existing 240 V circuit (up to USD 190), and stone wool batts in place of board in the base (about USD 100), together about USD 830, which would bring the estimate to about USD 3,040, still far over the target; only the reduced-scale test article (archived, on hold with TRL 4) comes near it.

## Decisions made

| Date | Decision | Decided by | Record |
| --- | --- | --- | --- |
| 2026-09-24 | Build a reduced-scale test article first, within the prototype budget | Amish | TBK-PRB-001, section 5 |
| 2026-09-25 | Test article budget USD 727.70; revisit the full-scale budget with its results (both on hold with TRL 4) | Amish: "i accept all your recommendations, go with them across all repos." | [TBK-DDR-002](decisions/0002-recommendations-accepted.md), A1, A2 |
| 2026-09-25 | Design decisions D1 to D8: silica sand 150 to 450 °C, cartridge heaters in capped wells, twelve 250 W wells, closed U-tubes, cold-side damper with mixing tee and heat trap, wells end at the lid, AES hot face with stone wool, 240 V burst-fire SSRs with contactor | Amish, same instruction | [TBK-DDR-002](decisions/0002-recommendations-accepted.md), A3 |
| 2026-09-25 | Requirement targets R1 to R20 as written, including the 500 °C drum-wall limit | Amish, same instruction | [TBK-DDR-002](decisions/0002-recommendations-accepted.md), A4, A5 |
| 2026-09-25 | R3 charge-time miss: choose the fix after the test article measures sand conductivity (on hold with TRL 4) | Amish, same instruction | [TBK-DDR-002](decisions/0002-recommendations-accepted.md), A6 |
| 2026-09-25 | Controller board stays deferred; KiCad install on hold with TRL 4 | Amish, same instruction | [TBK-DDR-002](decisions/0002-recommendations-accepted.md) |
| 2026-09-30 | The design is made physically buildable as the build plan is drawn | Amish: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." | [TBK-DDR-003](decisions/0003-design-for-construction.md) (its changes accepted on 2026-10-02, below) |
| 2026-09-30 | Outstanding decisions live in this register, not in the build plan | Amish: "don't log outstanding decisions in this build plan - that is not the place for it." | This register |
| 2026-10-01 | Budgets are value-engineering targets, not limits | Amish: "the budgets are a hypothethical control target to ensure we are thinking along a value engineering lens." | This register, Value engineering |
| 2026-10-02 | Design for construction accepted: the changes P1 to P11 and their knock-on changes, as made | Amish: "i approve your recommendations for all 555 open decisions." | TBK-DDR-003, Table 1 |
| 2026-10-02 | Warning labels: one BOM line, about USD 15, for hot-surface and 240 V warning labels on the jacket, outlet guard, junction box and enclosure (option a) | Amish: "i approve your recommendations for all 555 open decisions." | TBK-DDR-003, C1; REVIEW 2026-09-26, item 4 |
| 2026-10-02 | Air path beyond the unit: the layout stays illustrative at TRL 3 (option a), and its siting rules become requirements an installer must meet: the hot outlet duct is kept 450 mm from combustibles and guarded by a perforated steel sleeve, the outlet run forms a heat trap, and the fan sits below the mixing tee | Amish: "i approve your recommendations for all 555 open decisions." | TBK-DDR-003, C2; REVIEW 2026-09-26, item 2 |
| 2026-10-02 | Standby loss: 459 W standby loss accepted for now (option a); the stainless upper inlet legs and microporous hot face (357 W, about USD 450) are decided together with the R3 charge-time fix once the test article has measured loss | Amish: "i approve your recommendations for all 555 open decisions." | TBK-PRC-001, section 9; TBK-CAL-001, Table 5 |
| 2026-10-02 | Ground-fault protection: a 2-pole 5 mA GFCI breaker; 30 mA equipment ground-fault protection only if the heaters still trip it after bake-out and the installing electrician confirms the code allows it at that location | Amish: "i approve your recommendations for all 555 open decisions." | TBK-PRC-001, sections 8 and 9 |
| 2026-10-02 | The 80 degree cut sector is kept for the hero and detail renders only; drawings and STEP files stay whole | Amish: "i approve your recommendations for all 555 open decisions." | REVIEW 2026-09-26, item 1 |
| 2026-10-02 | Fan, guard sleeve, intake and grille sizes in the renders accepted as placeholders until the fan is chosen | Amish: "i approve your recommendations for all 555 open decisions." | REVIEW 2026-09-26, item 3 |
| 2026-10-02 | The teal top trim ring and kick plinth are optional cosmetic parts with no BOM line; the renders must also show the functional black outlet trim ring (BOM line 44) | Amish: "i approve your recommendations for all 555 open decisions." | REVIEW 2026-09-26, item 4 |
| 2026-10-02 | The insulation stays drawn as an AES hot face over stone wool | Amish: "i approve your recommendations for all 555 open decisions." | REVIEW 2026-09-26, item 5 |
| 2026-10-03 | Cost overrun accepted: the full-scale estimate of USD 3,869 against the USD 728 target (USD 3,141 over) | Amish: "Cost over target - i accept all the cost variations and overruns" | [REVIEW.md](REVIEW.md), session 2026-10-03 |
