---
doc_id: TBK-DDR-002
title: ThermaBrick recommendations accepted
project: ThermaBrick
doc_type: Design decision record
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-25'
  author: Amish Chadha
  change: Record the recommendations accepted by Amish on 2026-09-25, what changed in the repo, and the items still open
- version: "0.2"
  date: '2026-10-02'
  author: Amish Chadha
  change: 'Standby loss and GFCI choice decided by Amish on 2026-10-02 (TBK-DEC-001)'
---

# 0002: Recommendations accepted

- **Date:** 2026-09-25
- **Status:** accepted. Every item below that carried a recommendation is decided by Amish, 2026-09-25: go with recommendation. The two items still open then (standby loss and GFCI choice) were decided by Amish on 2026-10-02 (TBK-DEC-001).

## Context

On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." This record covers every ThermaBrick item that was "Proposed, awaiting Amish" and carried a recommendation, in `docs/REVIEW.md` (the September 2026 review and the 2026-09-25 rein-in session) and in TBK-PRC-001, Table 4. ThermaBrick has no TBK-DDR-001; the design proposals D1 to D8 were never written up as a separate record, so this record also serves as their design decision record. Where a recommendation offered several options, the recommended option is the decision. Items with no recommendation stay open.

The portfolio stays at TRL 3. Any decision that needs building, buying, testing or measurement is recorded as decided but on hold, because TRL 4 is on hold by Amish's instruction. The archived test article material under `archive/out-of-phase-trl4/` is frozen and was not edited.

## Decisions

Each item below is decided by Amish, 2026-09-25: go with recommendation.

| No. | Item | Recommendation adopted | Effect in this repo |
| --- | --- | --- | --- |
| A1 | Test article budget | Raise the accepted budget from $635.70 to $727.70, the BOM total after the build procedure's additions | `project.yaml` `budget_usd` 636 to 728; README budget line; TBK-PRB-001 v0.8, section 3 and section 5; TBK-REQ-001 v0.9, R20 restated; `bom/bom-notes.md`. On hold with TRL 4: nothing is bought |
| A2 | Full-scale budget | Revisit the full-scale budget with the test article's results | Recorded in TBK-PRB-001, section 5 and TBK-PRC-001, section 9. On hold with TRL 4 |
| A3 | D1 to D8, full-scale design (TBK-PRC-001, Table 4) | Accept all eight: silica sand, 150 to 450 °C (D1); cartridge heaters in capped wells (D2); twelve 250 W wells (D3); closed U-tubes (D4); cold-side damper, mixing tee and heat trap (D5); wells end at the lid (D6); AES hot face with stone wool bulk (D7); 240 V, 3.0 kW, burst-fire SSRs and contactor (D8) | TBK-PRC-001 v0.5, Table 4 status and section 8 text. No change to the geometry, BOM or calculations, because the design already embodies D1 to D8 |
| A4 | Full-scale design choices never reviewed (REVIEW.md, section 2.3) | Accept the storage window with the 550 °C well-wall limit; twelve 250 W heater wells, 1-1/4 in U-tubes, 50 mm AES blanket plus 267 mm stone wool | Already in TBK-PRC-001, TBK-CAL-001, `cad/src/model.py` and `bom/bom.csv`. No change |
| A5 | Requirement targets R1 to R20 (REVIEW.md, section 2.3) | Accept the targets as written, including R8's 500 °C drum-wall limit | TBK-REQ-001 v0.9 summary. R20 restated to follow A1 |
| A6 | Charge-time miss on R3 | Choose among cutting the loss, twelve 1 in wells (8.4 h) or relaxing R3 to 10 h only after the test article has measured sand conductivity | R3 stays **not met** at 9.6 h against 8 h. TBK-REQ-001 R3 and TBK-PRC-001 sections 8 and 9 record the path. On hold with TRL 4 |
| A7 | Test article design choices (REVIEW.md, section 2.3): 16 US gal drum, 68 kg of sand, four heater cells, one U-tube, 120 V, stone wool hot face, 12 V blower with dilution stack | Accept as proposed | Archived; decided but on hold with TRL 4 |
| A8 | Controller enclosure: 250 × 200 × 150 mm polycarbonate, HDR-15-12 DIN-rail supply, DPDT relay, REX-C100 independent limit, ungrounded thermocouples | Accept as proposed | Archived; decided but on hold with TRL 4 |
| A9 | Firmware safety rules: heaters off until the logging host connects; any fault switches the heater mode off; T1 trips at 575 °C and the sand at 560 °C | Accept as proposed | Archived; decided but on hold with TRL 4 |
| A10 | Test plan TBK-TST-001 pass criteria, tolerances and fitted power correction | Accept as proposed | Archived; decided but on hold with TRL 4 |
| A11 | Optional controller board (R-78E regulator, IRLZ44N, 2N3904) | Keep it optional and deferred, with the circuit choices as proposed | Archived; decided but on hold with TRL 4 |
| A12 | KiCad tooling | Install KiCad properly (`brew install --cask kicad`) before any schematic or board is regenerated | Needed only for the archived electronics; on hold with TRL 4 |

*Table 1. Items decided by Amish on 2026-09-25.*

Numbers before and after:

- `budget_usd`: 636 to 728.
- Test article budget: $635.70 accepted to $727.70 decided.
- TBK-REQ-001 status: 15 met, 3 open, 2 not met (R3, R20) to 16 met, 3 open, 1 not met (R3). R20 changed because its target was restated to the decided test article budget, not because the cost fell. The full-scale estimate stays $3,674.

## Still open

These items carried no recommendation and stayed open. Recommendations were written for them in the design decisions register (TBK-DEC-001), and Amish approved them on 2026-10-02 ("i approve your recommendations for all 555 open decisions."):

- **Standby loss.** Whether 459 W at full charge (8.7 kWh, 47 % of the window, over 24 h idle) is acceptable, or whether to adopt the stainless leg sections and microporous panel (TBK-CAL-001, Table 5: 357 W for about $450). TBK-PRB-001, section 5, item 2. Decided 2026-10-02: 459 W standby loss accepted for now (option a); the stainless upper inlet legs and microporous hot face (357 W, about USD 450) are decided together with the R3 charge-time fix once the test article has measured loss.
- **GFCI choice.** A 5 mA GFCI or 30 mA equipment ground-fault protection, to be chosen with the installing electrician (TBK-PRC-001, sections 8 and 9). Decided 2026-10-02: a 2-pole 5 mA GFCI breaker; 30 mA equipment ground-fault protection only if the heaters still trip it after bake-out and the installing electrician confirms the code allows it at that location.

Confirmations that need data, not a decision, also remain: the fan's pressure curve, the stone wool base board's compressive strength, and every price in the BOM.

## Consequences

- No geometry, BOM line or calculation changed, so `cad/src/model.py`, TBK-DWG-001 (Rev P1) and TBK-CAL-001 (v0.2) keep their revisions. They were regenerated only to refresh the title block footer.
- The repo stays at `trl: 3` and `trl_target: 3`.
- No cross-repo action arises from these decisions.
