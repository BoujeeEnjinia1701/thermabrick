# ThermaBrick review, September 2026

Prepared for Amish's review on 2026-09-24. It covers everything built since the v0.2 draft (commit `982233a`), every decision recorded on Amish's behalf, and every open issue. Nothing in this review adds scope.

**Where things stand.** The full-scale design is complete as a draft, but it misses its charge-time requirement (R3) by 1.6 h and loses 47 % of its stored heat in a day of standing. The reduced-scale test article is fully documented, from purchasing to the test report template, and none of it has been built or tested. Its BOM now totals $727.70. Amish accepted $635.70; the rise to $727.70 is proposed and awaits Amish's decision.

## 1. What was built since v0.2

| Commit | Work | Verified by | Not verified |
| --- | --- | --- | --- |
| `b575702` | Test article design: TBK-PRC-002, TBK-CAL-002, TBK-DWG-002, `cad/src/test_article.py`, `bom/bom-test-article.csv`. Corrected TBK-CAL-001 to v0.2 (see section 4) | CAD solids valid; sand mass checked in CAD within 0.4 % | Nothing built |
| `9823c32` | Test plan TBK-TST-001 (TP0 to TP6) | Renderer check | Not run |
| `9628cf2` | ESP32 firmware and logging host (`firmware/`) | 14 host unit tests pass; compiles for ESP32 with no warnings; logger checked against a mock controller | Never run on an ESP32 |
| `2c9b262` | Analysis script `docs/05-tests/tbk_tst_001_fit.py` | Synthetic self-test recovers known values (two seeds) | No real data yet |
| `a5ae50d` | Controller schematic TBK-DWG-003, generated from `electronics/src/schematic.py` | KiCad ERC 0 errors, 0 warnings; all 36 nets checked against the netlist | Not wired |
| `b37fd78` | Optional controller board TBK-DWG-004, gerbers | KiCad DRC 0 errors, 0 warnings, 0 unconnected, schematic parity clean | Not fabricated; now deferred |
| `412cf5d` | Controller enclosure model TBK-DWG-005; schematic to Rev P2 (DIN-rail supply) | Fit check at 3 mm clearance, including three deliberate faults it caught | Part envelopes from supplier listings, not measured |
| `24cfbd1` | Recorded Amish's decision to accept $635.70 | | |
| `08a839f` | Purchasing checklist, generated from the BOM | Totals match the BOM | Prices are estimates, not quotes |
| `a4b95ba` | Build procedure and generated cut list (`docs/07-build/`); TBK-DWG-002 to Rev P2; four BOM additions | Cut list generated from the models and schematic | Not used on a build |
| `45bdd0f` | Build log template and entry helper | Helper tested on a scratch copy | No entries yet |
| `d8c6256` | Test report template TBK-TST-002 and fill script | Dry run on self-test results | No real data yet |

*Table 1. Work since v0.2.*

**Software installed on this machine for this work:**

- through Homebrew: `uv`, `pango` and `cairo`;
- as a `uv` tool: PlatformIO;
- a Python environment at `~/.venvs/ohp-kit`.

The KiCad install failed because the Homebrew package needs an administrator password. KiCad is running from the downloaded disk image, mounted at `/Volumes/KiCad` until the next restart.

## 2. Decisions

### 2.1 Made by Amish

| Decision | Date |
| --- | --- |
| Develop ThermaBrick to a v0.2 draft | 2026-09-24 |
| Build the 6 kWh reduced-scale test article, within $600 | 2026-09-24 |
| Budget option 1: accept the test article at $635.70, all parts at once | 2026-09-24 |
| Add the four items the build procedure found to the BOM | 2026-09-24 |
| Commit and push each step to `main` | 2026-09-24 |

*Table 2. Decisions made explicitly by Amish.*

### 2.2 Recorded on Amish's behalf, now returned to "proposed, awaiting Amish"

| Item | Where it was recorded as accepted | Now |
| --- | --- | --- |
| Test article budget of $727.70 | TBK-PRB-001, TBK-REQ-001 R20, TBK-PRC-002, BOM notes, purchasing checklist, README, `project.yaml` (budget 728) | Proposed, awaiting Amish. Accepted budget stays $635.70; `project.yaml` is back to 636 |
| Full-scale design decisions D1 to D8 | TBK-PRC-001, Table 4 | Each marked "Proposed, awaiting Amish" |

*Table 3. Items reverted in this pass.*

### 2.3 Design choices never reviewed

These were never labeled as accepted, but Amish has not reviewed them. All live in Draft documents and remain proposals.

- **Storage window:** 150 °C to 450 °C, with a 550 °C well-wall limit for the quartz inversion margin.
- **Full scale:** twelve 250 W heater wells, 1-1/4 in U-tubes, and 50 mm AES blanket plus 267 mm stone wool.
- **Test article scale and cuts:** a 16 US gal drum, 68 kg of sand, four heater cells, one U-tube, 120 V plug-in, stone wool as the hot face, and a 12 V blower with a dilution stack.
- **Controller enclosure:** 250 × 200 × 150 mm polycarbonate, with a DIN-rail Mean Well HDR-15-12, a DPDT JQX-30F relay, a REX-C100 as the independent limit, and ungrounded thermocouples.
- **Firmware safety rules:** heaters stay off until the logging host connects; any fault switches the heater mode off; T1 trips at 575 °C and the sand at 560 °C.
- **Test plan:** the pass criteria and tolerances in TBK-TST-001, and the fitted power correction in its analysis.
- **Requirements:** the targets for R1 to R20 in TBK-REQ-001, including R8's 500 °C drum-wall limit.
- **Optional controller board:** its circuit choices (R-78E regulator, IRLZ44N, 2N3904).

## 3. Open issues

1. **Charge time misses R3.** With standby loss included, the full-scale unit fills in 9.6 h against the 8 h target, and stores 10.9 kWh in 4 h against 11 kWh (TBK-CAL-001 v0.2). If the sand conducts 20 % less than assumed, the fill takes 12.1 h. There are three options (TBK-PRC-001, section 8): cut the loss, use twelve 1 in wells (8.4 h), or relax R3 to 10 h. The test article is meant to measure the sand conductivity before a choice is made.
2. **Standby loss is 47 % of the stored heat per day.**
   - **Full scale:** loses 459 W at full charge, or 8.65 kWh over 24 h idle, 47 % of the 18.3 kWh window.
   - **Test article:** loses 249 W, 69 % in 24 h.
   - **Where it goes:** the heat is released into the room, so the unit must stand inside the heated space, but it cannot be switched off.
   - **Options:** stainless upper inlet legs and a microporous hot face would bring the full-scale loss to 357 W (7.1 kWh per day) for about $450 (TBK-CAL-001, Table 5).
   - **Decision needed:** whether the loss is acceptable is an open decision in TBK-PRB-001.
3. **The test article budget has risen from $600 to $727.70.** Every step came from correcting a real gap, not from added features:

   | Stage | Total |
   | --- | --- |
   | First estimate | $599.50 |
   | Pull-down resistors added | $599.70 |
   | Enclosure fit check, which replaced a $10 enclosure too shallow for the REX-C100 and a barrel-jack supply, and added glands, DIN rail and connectors | $635.70, accepted by Amish |
   | Build procedure: second stone wool pack, heater cable, wiring consumables, thermocouple extension | $727.70, proposed |

   The optional board would take it to $752.55. The full-scale BOM is $3,673.50, about six times the original $600 target.
4. **The full-scale CAD model had one invalid solid. Fixed after this review was written, at Amish's request.** The U-tube at 270° failed the BRep validity check, because building each tube at its own angle let near-zero sine and cosine terms defeat the boolean. The model now builds one U-tube along +X and rotates copies into place. All six tubes are valid and identical (935.34 cm³), the assembly is valid, and the re-exported STEP reads back as 47 valid solids. The design geometry is unchanged. The regenerated TBK-DWG-001 differed from the committed sheet by one pixel in 2.26 million, so the sheet was not reissued.
5. **TRL is not recorded.** Section 9 of the standard is in the newer kit (1.1.x) used by the other portfolio repos. ThermaBrick still runs kit 1.0.0, which has no section 9, and its `render.py --check` does not check TRL. The TRL 3 evidence is otherwise complete:
   - calculation notes TBK-CAL-001 and TBK-CAL-002;
   - the build123d model and its STEP export;
   - drawing sheets TBK-DWG-001 to TBK-DWG-005;
   - fully priced BOMs, with no empty unit cost in 89 lines.

   When this review was written, the invalid solid in item 4 meant the "working model" condition was not fully met, so `trl`, `trl_target` and `trl_evidence` were not added to `project.yaml`. With item 4 fixed, the TRL 3 evidence is complete. **Update after the review:** at Amish's request the kit was synced to 1.1.4 and `trl: 3` recorded, with the build log entry `build-log/2026-09-24-trl-3-recorded.md`. **Second update:** at Amish's request the kit was then synced to 1.2.0 (option A): `trl_target` is now 3 under the portfolio cap in `.kit/PHASE.yaml`, and the required concept media are generated in `media/` by `cad/src/concept_media.py` (concept sheet TBK-DWG-006 Rev P1). Recorded in `build-log/2026-09-24-kit-1-2-0.md`. The 1.2.0 check warns that the test article work is beyond the TRL 3 cap; it is kept and not extended. The 1.1.4 check would also pass an unsupported `trl: 4` here, because it counts the test plan and the build log's `README.md` and `TEMPLATE.md` as TRL 4 evidence. That weakness belongs in the kit source. Section 9 also requires every change of TRL to be recorded in the build log. That would be a new entry, which this pass does not create.
6. **Nothing physical has been verified.** Specifically:
   - **Prices:** estimates from US list prices, not quotes.
   - **Heaters:** made-to-order imports with a two to four week lead time and untested quality.
   - **SSR:** counterfeits are common.
   - **Blower:** its curve is assumed.
   - **Enclosure parts:** sized from supplier listings, not measured.
   - **Firmware:** never run on an ESP32.
   - **Controller board:** never fabricated.
7. **Design risks carried forward:**
   - sand ratcheting and drum growth (R19);
   - GFCI nuisance trips from the MgO heaters;
   - a drum-wall hot spot of about 480 °C beside the outer wells, estimated but not resolved by the 1D model;
   - stone wool used at a 450 °C hot face in the test article, which burns off its binder;
   - the full-scale AES blanket, which the test article does not test.
8. **Model limitations.** The radial cell model treats each pipe's share of sand as a circle, spreads the standby loss evenly, and lumps axial effects. The fit intervals are optimistic. The TP5 self-test checks the code path, not the physics.
9. **Documentation gaps:**
   - D1 to D8 are not yet design decision records.
   - TBK-TST-002 is an empty template.
   - `project.yaml` still says `status: concept`.
   - Nothing has been tagged or released.
10. **Tooling:** KiCad needs a proper install before any schematic or board can be regenerated after a restart:

    ```bash
    brew install --cask kicad
    ```

## 4. Errors found and corrected along the way

| Error | Found by | Correction |
| --- | --- | --- |
| TBK-CAL-001 v0.1 left standby loss out of the charge and discharge runs. It claimed a 7.9 h charge and 1.0 kW for 18 h | Test article sizing | CAL-001 v0.2: 9.6 h and 14.3 h; R3 marked not met |
| Test article thermocouples left too low: tips at 245 mm would put the 500 mm probes' lead junctions in the hot insulation | Build procedure | Tips at 300 mm (TBK-TST-001 v0.4) |
| Wells listed as 717 mm long | Cut list | 692 mm (667 mm finished plus 25 mm crimp) |
| Base bricks overlapped at the drum center in the model | Cut list | Moved under the chime (TBK-DWG-002 Rev P2) |
| U-tube legs modeled 80 mm above the jacket; the shortest stock nipple that reaches gives 152 mm | Cut list | Model and TBK-DWG-002 Rev P2 |
| Enclosure 100 mm deep, which cannot take the REX-C100 | Enclosure fit check | 250 × 200 × 150 mm |
| 12 V supply specified as a barrel-jack adapter | Enclosure model | DIN-rail HDR-15-12; TBK-DWG-003 Rev P2 |
| Relay not specified as double pole; pull-downs missing from the BOM; earth bonding unspecified | Schematic | BOM and TBK-PRC-002 corrected |
| Glands, DIN rail, connectors, earth stud, second insulation pack, heater cable, wiring consumables and thermocouple extension missing from the BOM | Enclosure model and build procedure | Added |
| Grounded-junction thermocouples not excluded, which risked a ground loop | Purchasing checklist | Specified as ungrounded |
| This review's first commit (`b2bc80a`) pushed four revision rows whose unquoted "Review pass:" text broke the YAML front matter; a piped command hid the failing check | Re-running the check with its exit status | Rows quoted and PDFs rendered in the following commit |

*Table 4. Errors and corrections.*

## 5. Changed in this review pass

- **This document:** added as `docs/REVIEW-2026-09.md`; renamed `docs/REVIEW.md` at Amish's request on 2026-09-24, as kit 1.2.0 expects.
- **Budget:** $727.70 returned to proposed in TBK-PRB-001 (v0.7), TBK-REQ-001 (v0.8), TBK-PRC-002 (v0.11), the BOM notes, the purchasing checklist, the README, and `project.yaml` (budget back to 636).
- **Design decisions:** D1 to D8 in TBK-PRC-001 (v0.4) marked "Proposed, awaiting Amish".
- **Controller board:** marked optional and deferred in TBK-PRC-002, the README, the BOM notes, the purchasing checklist and `electronics/README.md`.
- **Attribution:** the two decisions Amish made are now attributed to Amish by name.
- **TRL:** not added (section 3, item 5).

## 6. Awaiting Amish

1. Accept, cut or reject the $727.70 test article budget.
2. Review design proposals D1 to D8 and the unreviewed choices in section 2.3.
3. Choose a path on the R3 charge-time miss, or wait for the test article's measurements.
4. Decide whether 47 % daily standby loss is acceptable, or adopt the loss-reduction options.
5. Confirm the controller board stays deferred.
6. Done after the review: the U-tube solid is fixed, TRL 3 is recorded, and the kit is on 1.2.0 with `trl_target: 3`.
7. Install KiCad properly.
8. Done: renamed to `docs/REVIEW.md` at Amish's request, as kit 1.2.0 expects.
