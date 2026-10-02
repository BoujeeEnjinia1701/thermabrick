---
doc_id: TBK-DDR-003
title: ThermaBrick design for construction
project: ThermaBrick
doc_type: Design decision record
version: "0.1"
status: Draft
date: '2026-09-30'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
- version: "0.1"
  date: '2026-09-30'
  author: Amish Chadha
  change: Changes that make the concept physically buildable, with the reason for each; made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review
---

# 0003: Design for construction

- **Date:** 2026-09-30
- **Status:** Draft. Made under Amish's 2026-09-30 instruction to make the design physically buildable; open for his review. The items in Table 3 are proposed, awaiting Amish.

## Context

On 2026-09-30 Amish asked for an illustrated build plan for every repo and wrote: "If you are realising that the design cannot be built as per concept - fix the design assumptions to match and be physically feasible as you draw the illustrations." The v0.2 model of ThermaBrick (TBK-PRC-001, TBK-DWG-001 Rev P1) showed what the unit does and sized it correctly, but a constructability review of `cad/src/model.py` and `bom/bom.csv` found eleven places where it could not be built, fixed or assembled as drawn (P1 to P11 below).

The changes keep what ThermaBrick does: the same drum, sand mass and depth, heater layout and rating, U-tube positions and bore, insulation thicknesses, envelope (1,209 mm by 1,462 mm), air path, controls and safety chain. Nothing here changes the pitch or the safety case; P1 is chosen specifically so that the drum-wall temperature case (R8) is unchanged. Every change is in `cad/src/model.py`, which now runs 72 constructability checks (`python cad/src/model.py --check`): parts that must not overlap do not; parts that stand on or are fixed to another touch it; holes, gaps, cut lengths, lead lengths and the firebrick count meet the stated limits; every part is a valid solid. All 72 pass.

## Decision

*Table 1. Changes made to the model, the BOM and the calculations.*

| # | Problem in the concept | Change made | Why this way |
| --- | --- | --- | --- |
| P1 | The heater wells hung 14 mm above the drum floor with nothing under them. The BOM cut length (906 mm) did not match the model (876 mm). | Each well stands on its cap on a levelled 14 mm first lift of sand, at the concept height; cut length 876 mm. | Standing the caps on the steel floor would put the hottest part of the bed in metal contact with the drum, against the R8 drum-wall case; a levelled sand lift supports the wells and keeps that case unchanged. |
| P2 | The U-tube bottoms floated 50 mm above the floor. Two 1-1/4 in elbows and the 2-1/2 in nipple in the BOM set the legs 118 mm apart, not the 155 mm the model and calculations use. The BOM leg lengths (1,149 and 901 mm) did not match the model. | Each U-tube is two malleable iron elbows and a 1-1/4 x 4 in nipple (155.6 mm between leg centres); the elbows rest on the drum floor, the run 28 mm above it. Leg cut lengths 1,175 mm (inlet) and 866 mm (outlet). | A 4 in nipple is the stock size that gives the 155 mm spacing. Resting on the floor gives every U-tube a firm seat during the fill. The U-tube carries no heat source, so floor contact does not change R8. |
| P3 | Lid holes 1 mm larger than the pipes in radius: 24 sand-set pipes cannot all pass at once, and the well-wall thermocouples T1 to T3 had no way through. | Well holes 36 mm (4.65 mm radial gap, enough for a 3 mm sheath beside the well), leg holes 48 mm (2.9 mm), four 6 mm holes for T4 to T7. An AES rope collar is laid round every pipe on the lid. | The lid can be lowered over every pipe; the rope collar keeps the headspace closed as the concept intended (the bed still breathes; no pressure). |
| P4 | The concept used the lid "as a top template on spacers" during the sand fill, but sand cannot be poured with the lid in place. | A plywood setting template (18 mm, 597 mm disc) drilled like the lid, with an 80 mm centre pour hole and four 64 mm pour holes, sits on the drum rim during the fill and is lifted off before the headspace insulation. New BOM line 43. | A temporary jig is the simplest way to hold 24 pipes and four sheaths upright and in place until the sand locks them. Every pour hole is at least 10 mm from a pipe or sheath hole. |
| P5 | The base was one solid cylinder. The firebrick course "under the drum footprint" left a void out to the jacket at the firebrick and AES levels, and 14 bricks cannot be cut to cover the footprint. | Firebrick laid flat and cut to a 610 mm disc (19 pieces from 15 bricks; 16 bought, one spare), an AES board disc of 610 mm on it, and a ring of 89 mm stone wool batt from 610 mm out to the jacket. | The drum's 597 mm bottom rim stands 6 mm inside the AES disc, over the firebrick that carries the load (15.0 kPa, safety factor 4 on the 60 kPa board). The 89 mm batt equals the 64 mm brick plus 25 mm AES board, so the base is level. |
| P6 | The inlet plenum was 110 mm tall, leaving 4 mm of wall above and below the 4 in collar, the collar's bore did not pass through the wall, and the plenum had no fixing to the cap. | Plenum 140 mm tall, a 4 in hole cut in the outer wall behind the collar, and 15 mm flanges folded out (outer wall) and in (inner wall), riveted to the cap and sealed with foil tape. The inlet legs are 30 mm longer to end 10 mm below its top. | 19 mm of wall each side of the collar takes the crimped collar's rivets. The overall height is unchanged because the plenum stays below the 160 mm outlet stub. |
| P7 | The collector ring had no fixing to the lid, and a continuous flange is impossible because the inner ring of wells passes 9.6 mm outside it. | Six tabs folded out at the foot of the ring, between the wells (at 30, 90, 150 ... degrees), each with one steel pop rivet into the lid; AES rope round the foot. The 18 ga top disc has a folded edge riveted to the ring. | Uses the stovepipe's own metal; steel rivets, not aluminium, in the hot zone (R13). |
| P8 | The galvanized jacket cap was drawn touching the 4 in outlet, which carries air at up to 314 °C, against R13 (no zinc above 200 °C). | A 180 mm clearance hole in the cap, the 39 mm gap packed with AES blanket, and a 250 mm black (uncoated) steel trim ring screwed to the cap over it. New BOM line 44. | Keeps zinc 39 mm from the hot pipe behind insulation, the same practice as a stovepipe passing a combustible surface. The cap-edge temperature is to be confirmed at the first firing (TBK-DEC-001). |
| P9 | The heaters' 36 in (914 mm) leads reach only about 350 mm sideways after rising out of the wells and the top insulation, but the farthest well is about 680 mm from the junction box; the box had no position in the model. | Heaters specified with 72 in (1,829 mm) ceramic-beaded leads (needs up to 1,593 mm with a 30 % routing allowance). Junction box on the cap at 120 degrees, 430 mm out, over a 40 mm grommeted hole; four screws. New BOM line 46 (grommets). | Longer leads are a standard option on made-to-order cartridge heaters. The box sits clear of the plenum (60 mm) and on the cool cap. |
| P10 | The thermocouples had no lid holes and no route out; the centre sand thermocouple T4 sat under the collector and outlet; 1,000 mm sheaths could not reach outside the jacket. | T1 to T3 tied to their wells and passing through the well holes; T4 rises from the centre to the sand surface and is bent once to cross between two outlet legs to a lid hole 165 mm out at 51 degrees; T5 to T7 at their stated positions, each tied to a stainless guide rod standing on the floor (new BOM line 45); T8 through a 4 mm hole in the collector top. Sheaths 1,500 mm, spare length coiled in the top insulation, leaving through one 25 mm grommet in the cap at 95 degrees, 330 mm out. | Mineral-insulated sheaths can be bent by hand. The measuring points of TBK-PRC-001 Table 3 are kept. |
| P11 | The jacket cap had no fixing, yet it must come off to replace a heater (R17), and it was drawn as one 1,210 mm disc although the flashing is 610 mm wide. | Cap made from three 610 mm strips lapped 25 mm and riveted, cut to a 1,260 mm disc with a 25 mm skirt turned down over the side, held by eight stainless sheet metal screws. | Screws let the cap, plenum and junction box lift off together for heater service; the side stays riveted. |

*Table 2. Knock-on changes.*

| Item | Change | Reason |
| --- | --- | --- |
| Mass | Insulation estimate 75 to 80 kg (base batt ring, two more firebricks); operating mass 415 kg (was 410 kg), within R15's 450 kg. Firebrick load 15.0 kPa (was 14.8 kPa). | TBK-CAL-001 v0.3, section 7, re-run with the sizing script. |
| Thermal and electrical | Unchanged. The changes alter no input of the sizing model. The U-tube runs sit 22 mm lower in the bed, which the one-dimensional model does not resolve. | TBK-CAL-001 v0.3 |
| Cost | BOM $3,853.50 (was $3,673.50, +$180.00): longer heater leads (+$48), longer thermocouples (+$32), 4 in nipples (+$12), two firebricks (+$12), second AES rope (+$20), fasteners (+$5) and lines 43 to 46 (+$51). Value-engineering target: USD 728. Estimated cost of the constructable design: USD 3,854 (USD 3,126 over the target). | `bom/bom.csv`, `bom/bom-notes.md` |
| Drawing | TBK-DWG-001 Rev P2; making sketches TBK-DWG-101 to TBK-DWG-110 added. | Follows the model. |
| Documents | TBK-CAL-001 v0.3, TBK-PRC-001 v0.6, TBK-REQ-001 v0.10, TBK-PRB-001 v0.9: mass, cost, build summary, R13, R15, R17 and R20 notes. No requirement changed status: R3 stays not met (9.6 h against 8 h). | Follows the model. |

*Table 3. Proposed, awaiting Amish.*

| # | Question | Options | Recommendation |
| --- | --- | --- | --- |
| C1 | Hot-surface and 240 V warning labels have no BOM line, though the appearance model shows them (REVIEW 2026-09-26, item 4) and they are a safety item. | (a) add one BOM line for the labels, about USD 15; (b) leave to the installer. | (a). |
| C2 | The air path beyond the unit (hot duct route, tee and fan position, control enclosure on the wall) is drawn in the build plan from the illustrative layout of the appearance model (REVIEW 2026-09-26, item 2); real sites differ. | (a) keep it illustrative, with the rules the plan states (450 mm from combustibles, guard, heat trap, fan below the tee); (b) add an installation layout sheet. | (a) at TRL 3. |

## Consequences

- `design_state: constructable` in `project.yaml`. The build plan TBK-BLD-001 (`docs/05-build-plan.md`) shows every component and step in pictures generated from the model (`cad/src/build_plan_media.py`); open items are in the design decisions register TBK-DEC-001 (`docs/06-design-decisions.md`).
- STEP and STL exports (`cad/step/thermabrick.step`, `cad/stl/thermabrick.stl`), TBK-DWG-001 Rev P2 and the concept media are regenerated from the changed model.
- The photoreal renders (`media/render-*.png`), `media/card.png`, `media/social-preview.png` and the appearance model `cad/src/product_model.py` still show the concept base, a 110 mm plenum, no trim ring and no cap fixings. They are made on Amish's Mac and are now stale.
- The test article (TBK-PRC-002, archived) was not touched.
