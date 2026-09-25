# 2026-09-24: TRL 3 recorded

| Field | Entry |
| --- | --- |
| Date | 2026-09-24 |
| Author | Amish Chadha |
| Stage or procedure | Project record: Technology Readiness Level (`.kit/STANDARDS.md`, section 9) |
| Hours | |
| Room temperature | Not applicable |
| Repo commit | `a07b0c2` |

## Goal

Record ThermaBrick at TRL 3 (analytical proof of concept), at Amish's request, with the evidence that section 9 requires.

## Work done

1. Synced the portfolio kit from 1.0.0 to 1.1.4, which adds section 9 and makes `python .kit/render.py --check` verify the claimed TRL. The 1.1.4 copy was taken from `wastewise-scan` at commit `d5cba39`, the commit that adopted 1.1.4.
2. Fixed the invalid U-tube solid in the full-scale model (commit `a07b0c2`), which had been the one gap in the TRL 3 evidence.
3. Added `trl: 3`, `trl_target: 4` and `trl_evidence` to `project.yaml`.
4. Added `environment: lab` to the TST front matter, as kit 1.1.4 requires.

## Records

| Quantity | Expected | Measured | OK |
| --- | --- | --- | --- |
| TRL 1: problem statement (PRB) | Present | TBK-PRB-001 v0.7 | Yes |
| TRL 2: precis (PRC) and requirements (REQ) | Draft present | TBK-PRC-001 v0.4, TBK-REQ-001 v0.8 | Yes |
| TRL 3: calculation note (CAL) | Present | TBK-CAL-001 v0.2 (and TBK-CAL-002 for the test article) | Yes |
| TRL 3: working build123d model | Builds, all solids valid | `cad/src/model.py`: assembly valid after `a07b0c2` | Yes |
| TRL 3: STEP export | Present and readable | `cad/step/thermabrick.step`: reads back as 47 valid solids | Yes |
| TRL 3: drawing sheet (DWG) | Present | TBK-DWG-001 Rev P1 (and TBK-DWG-002 to TBK-DWG-005) | Yes |
| TRL 3: priced BOM | Every unit cost filled in | `bom/bom.csv`: 42 lines, all priced, $3,673.50 | Yes |
| Kit check | Passes at TRL 3 | `render.py --check` passes with kit 1.1.4 | Yes |

## Deviations

| What differs | Why | Document to update | Done |
| --- | --- | --- | --- |
| None | | | |

## Problems and fixes

The TRL 3 evidence was first found incomplete in the September 2026 review (`docs/REVIEW-2026-09.md`, section 3, item 5). The full-scale model carried one invalid U-tube solid, fixed in `a07b0c2`.

TRL 3 is a documentation claim. It does not mean the design meets its requirements: the full-scale unit still misses R3 (a 9.6 h charge against 8 h), and its standby loss is 47 % of the stored heat per day. Both are open in the review.

## Parts and cost

| BOM item | Qty | BOM estimate (USD) | Paid (USD) | Supplier |
| --- | --- | --- | --- | --- |
| None | | | | |

## Photos

None.

## Safety

None.

## Next steps

- [ ] TRL 4 needs hardware: build the test article, run TBK-TST-001, and complete TBK-TST-002 with `environment: lab`, supported by build log entries.
- [ ] Kit 1.1.4's TRL 4 check is too weak. With `trl: 4` set temporarily, `render.py --check` passed for this repo with no hardware built. It counts any TST document (the test plan qualifies) and any two `.md` files in `build-log/` (`README.md` and `TEMPLATE.md` qualify). The fix belongs in the kit source, not this repo; `trl` was restored to 3.
- [ ] Kit 1.2.0 exists in `wastewise-scan` (commit `8ee209e`, "TRL 3 cap, CLAUDE.md guardrails, concept media standard"); syncing to it is for Amish to decide.
