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
| Test article budget of $727.70 | TBK-PRB-001, TBK-REQ-001 R20, TBK-PRC-002, BOM notes, purchasing checklist, README, `project.yaml` (budget 728) | Proposed, awaiting Amish at the time. Decided by Amish, 2026-09-25: go with recommendation ($727.70; `project.yaml` 728; TBK-DDR-002) |
| Full-scale design decisions D1 to D8 | TBK-PRC-001, Table 4 | Each marked "Proposed, awaiting Amish" at the time. Decided by Amish, 2026-09-25: go with recommendation (TBK-DDR-002) |

*Table 3. Items reverted in this pass.*

### 2.3 Design choices never reviewed

These were never labeled as accepted when this review was written. Decided by Amish, 2026-09-25: go with recommendation (TBK-DDR-002, items A4 to A11); the test article, enclosure, firmware, test plan and board items are on hold with TRL 4.

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

1. Accept, cut or reject the $727.70 test article budget. Decided by Amish, 2026-09-25: go with recommendation ($727.70; on hold with TRL 4).
2. Review design proposals D1 to D8 and the unreviewed choices in section 2.3. Decided by Amish, 2026-09-25: go with recommendation (TBK-DDR-002).
3. Choose a path on the R3 charge-time miss, or wait for the test article's measurements. Decided by Amish, 2026-09-25: go with recommendation (wait for the test article's measurements; on hold with TRL 4).
4. Decide whether 47 % daily standby loss is acceptable, or adopt the loss-reduction options. No recommendation made; still proposed, awaiting Amish.
5. Confirm the controller board stays deferred. Decided by Amish, 2026-09-25: go with recommendation (deferred; archived).
6. Done after the review: the U-tube solid is fixed, TRL 3 is recorded, and the kit is on 1.3.1 with `trl_target: 3`.
7. Install KiCad properly. Decided by Amish, 2026-09-25: go with recommendation; on hold with TRL 4, since the electronics are archived.
8. Done: renamed to `docs/REVIEW.md` at Amish's request, as kit 1.2.0 expects.

## 7. Log

- 2026-09-24: kit synced to 1.3.0 at Amish's request. Concept media regenerated with a scale figure, a 3D viewer (`media/model.glb`, `media/viewer.html`) and a heat flow diagram (`media/flow.png`, TBK-CAL-001 estimates); TBK-DWG-006 reissued at Rev P2. Recorded in `build-log/2026-09-24-kit-1-3-0.md`.
- 2026-09-24: kit synced to 1.3.1 at Amish's request. Only `media/flow.png` changed (new layout, same values). Recorded in `build-log/2026-09-24-kit-1-3-1.md`.

## Session 2026-09-25: rein-in to TRL 3

Done at Amish's instruction ("yes" to the rein-in recommendation, 2026-09-25). TRL 4 is on hold for the whole portfolio.

**What was done**

- Moved all TRL 4 material to [archive/out-of-phase-trl4/](../archive/out-of-phase-trl4/README.md) with `git mv`, keeping history and deleting nothing: the test article precis, sizing, drawings, models and BOMs; test plan and report template; build procedure and cut list; KiCad schematic, controller board and Gerbers; firmware and logging host; purchasing checklist; build-log template and helper.
- `cad/src/sheets.py` now builds TBK-DWG-001 only. The archived copy builds the test article and enclosure sheets.
- README: links to archived items removed and an archive note added.
- `project.yaml`: `trl: 3`, `trl_target: 3` unchanged. The `trl_evidence` list already pointed only at TRL 3 files (TBK-CAL-001, the model, STEP, TBK-DWG-001, `bom/bom.csv`).

**Decisions**

- Unchanged and still Amish's: develop to a v0.2 draft; the test article budget of $635.70. That budget now applies to archived work and is on hold.
- Still "Proposed, awaiting Amish" at the time: the $727.70 test article budget; full-scale design decisions D1 to D8; the design choices in section 2.3. All three decided by Amish, 2026-09-25: go with recommendation (see the session below).

**Still open at TRL 3** (from section 3): R3 charge time (9.6 h against 8 h); 47 % standby loss per day; the full-scale budget ($3,674 against the $600 concept figure); design decision records for D1 to D8.

**Recommended next step.** Decide D1 to D8 and how to close R3 and the standby loss, all on paper. TRL 4 stays on hold; when it is lifted, the archived test article is the starting point.

## Session 2026-09-25: recommendations accepted

On 2026-09-25 Amish wrote: "i accept all your recommendations, go with them across all repos." Every item with a recommendation is now decided by Amish, 2026-09-25: go with recommendation. The full list is in [TBK-DDR-002](decisions/0002-recommendations-accepted.md).

**Decisions applied and what changed**

| Decision | Before | After |
| --- | --- | --- |
| Test article budget | $635.70 accepted; $727.70 proposed | $727.70 decided; on hold with TRL 4 |
| `project.yaml` `budget_usd` | 636 | 728 |
| R20 prototype cost | "About $600 USD in parts"; not met | Restated to the test article budget of $727.70 or less, full-scale cost reported; met (I) for the test article BOM ($727.70). Full-scale estimate unchanged at $3,674 |
| D1 to D8 (TBK-PRC-001, Table 4) | Proposed, awaiting Amish | Decided; TBK-DDR-002 is their design decision record |
| Section 2.3 design choices and R1 to R20 targets | Unreviewed proposals | Decided; test article, enclosure, firmware, test plan and board items on hold with TRL 4 |
| R3 charge-time path | Open | Decided: choose the fix after the test article measures sand conductivity; on hold with TRL 4. R3 stays not met (9.6 h against 8 h) |
| Full-scale budget | Revisit proposed | Revisit with test results decided; on hold with TRL 4 |
| Controller board | Deferred, to be confirmed | Kept deferred (archived) |
| KiCad install | Awaiting Amish | Decided; on hold with TRL 4 |

*Table 5. Decisions applied on 2026-09-25.*

No geometry, BOM line or calculation changed, because the full-scale design already embodied D1 to D8. `cad/src/model.py`, TBK-DWG-001 (Rev P1), TBK-CAL-001 (v0.2) and the concept media were regenerated only to refresh the footer, which now points to designmolecule.com.

Controlled documents changed: TBK-PRB-001 0.7 to 0.8; TBK-PRC-001 0.4 to 0.5; TBK-REQ-001 0.8 to 0.9; TBK-DDR-002 0.1 new. Also changed: `project.yaml`, `README.md` (budget line, hero image and links line, links to archived files corrected, and new sections "Concept rationale", "Burning platform", "Where it could be used" and "What sparked the idea"), and `bom/bom-notes.md`.

**Requirement status now (TBK-REQ-001 v0.9)**

- Not met (1): R3 charge time, 10.9 kWh in 4 h and full in 9.6 h against 11 kWh and 8 h.
- Open (3): R12 fail-safe behavior and R18 monitoring (firmware; archived and on hold), R19 durability (ratcheting, needs test).
- Met (16): R1, R2, R4 to R11, R13 to R17 and R20, by analysis, inspection or design; none tested.

**Still awaiting Amish** (no recommendation was made)

- Standby loss: accept 459 W at full charge (8.7 kWh, 47 % of the window, per day idle), or adopt the Table 5 options in TBK-CAL-001 (357 W for about $450).
- GFCI choice: 5 mA GFCI or 30 mA equipment protection, with the installing electrician.

**Cross-repo actions:** none.

**TRL.** `trl: 3` and `trl_target: 3` are unchanged. TRL 4 remains on hold by Amish's instruction: nothing was built, bought, tested or measured, and `archive/out-of-phase-trl4/` was not touched.

## Session 2026-09-26: sources strengthened

README "Where it could be used" and "What sparked the idea", per Amish's instruction of 2026-09-26 ("Fix the weaker sources"). Every link below was fetched and checked against the claim it supports.

| Item | Old source | New source |
| --- | --- | --- |
| United States (California) row, tariff claim | None | California Public Utilities Commission, "Net Energy Metering and Net Billing" (Net Billing Tariff from April 15, 2023, Decision D.22-12-056); US EIA curtailment link rechecked and kept |
| United States (Colorado and the Mountain West) row | None | Row removed; no credible source found for the climate claim within this session's search budget |
| Finland row | Wikipedia, "Thermal energy storage" (alone) | Polar Night Energy, "What is a Sand Battery?", with UNRIC alongside |
| Australia row | None | Clean Energy Council rooftop solar report, September 15, 2025, and SA Power Networks on AEMO-directed curtailment; the uncited "export limits common" and "cool winters" claims were dropped |
| Northern China row | None | Rewritten as "China" to state only what the IEA reports (*Renewables 2023*, Heat) |
| Ladakh, India row | None | Replaced by "Mongolia (Ulaanbaatar)": World Bank feature, June 26, 2018 (coal stoves, winter PM2.5 above 100 times the WHO 24-hour guideline) |
| What sparked the idea | Wikipedia, "Thermal energy storage" | Polar Night Energy, "World's first Sand Battery" and "What is a Sand Battery?"; UNRIC, "Sand warms up the Finnish polar night" |

Corrections from the primary source: the Kankaanpää unit is 200 kW and 8 MWh per Polar Night Energy, not the 0.1 MW that Wikipedia gave (UNRIC also gives 100 kW; the company figure is used). The "up to 600 °C" claim is now attributed to UNRIC (500 to 600 °C storage). The inspiration event is unchanged; its line in `INSPIRATIONS.md` was updated to the new sources. No controlled document changed; TBK-PRB-001 had no link to the weak source.

## Session 2026-09-26: product appearance model and photoreal renders

Amish chose this repo for the first batch of product renders on 2026-09-26. This session added `cad/src/product_model.py`, an appearance model for photoreal renders, and pointed the README hero at `media/render-hero.png` with a link to `media/render-exploded.png`. The render files are produced later by the orchestrator. No existing model, BOM, drawing or controlled document was changed.

**What `product_model.py` adds**

- `product_parts()`: 80 named parts (18 shell, 13 internal, 44 accessory, 5 context), each with colour, material, BOM line, group and explode offset; `TITLE` and three `RENDER_VIEWS` (hero, exploded, detail).
- Jacket finish: three lapped rows with riveted seams, a vertical lap seam, a teal top trim ring, a dark kick plinth, a name plate, and HOT SURFACES INSIDE and HOT OUTLET warning labels.
- An 80 deg cut sector at the front through the jacket, stone wool, AES blanket, drum, sand and base, showing the sand bed, two heater wells split open with lit cartridge heaters and their beaded leads, a U-tube, and the three base layers (stone wool board, insulating firebrick with joints, AES board).
- Inlet damper with its servo, intake bell mouth and grille on the plenum collar; heater junction box with lid, screws, gland and a DANGER 240 V label.
- Hot outlet duct as 4 in black stovepipe that rises and turns down as a heat trap, in a perforated guard sleeve with a HOT SURFACE label; mixing tee with the balancing damper and room-air grille; EC inline fan with collars, accent ring, rating label and lit run light, on a wall bracket; ribbed insulated flexible supply duct into a wall collar.
- Wall-mounted control enclosure with door, hinges, latch, name plate, 1/16 DIN high-limit readout (lit), charge, discharge and fault lights (charge lit) and a DANGER 240 V label.
- Context: a compact slab floor patch, a back wall patch, surface conduit and straps.

**Where the appearance model differs from `model.py`** (each one Proposed, awaiting Amish)

1. *Cut sector.* The renders remove an 80 deg sector (268 to 345 deg) to show the inside, and the two wells in it are split open. Recommendation: keep it for the hero and detail renders only; the drawings and STEP stay whole.
2. *Duct, fan and enclosure layout.* `model.py` ends at the 4 in outlet stub and the inlet collar. The route of the hot duct (toward 35 deg, drop at 800 mm radius, tee at 1,150 mm), the fan position and bracket, the supply duct into the back wall, the junction box position (120 deg, 430 mm radius) and the enclosure position on the wall are an appearance layout only. Recommendation: treat it as illustrative; add it to TBK-DWG-001 only if Amish wants an installation layout sheet.
3. *Sizes not in the design.* The fan body (236 mm diameter by 230 mm), guard sleeve (about 160 mm diameter), intake bell mouth and grille, and the room-air grille are assumed for appearance. Recommendation: accept as placeholders until the fan is chosen (open question on its pressure curve).
4. *Cosmetic items not in the BOM.* The teal top trim ring, kick plinth, name plates and warning labels have no BOM lines. Recommendation: add one BOM line for warning and rating labels, since hot-surface and 240 V labels are a safety item; treat the trim ring and plinth as optional cosmetic parts.
5. *Insulation split.* `model.py` draws all insulation as one body; the appearance model splits it into the AES hot face and the stone wool by the thicknesses in PARAMS. No dimension changes.

**TRL.** This is an appearance model only: no tolerances, fabrication detail, PCB layout or firmware. `trl: 3` and `trl_target: 3` are unchanged, and TRL 4 remains on hold by Amish's instruction.

## Session 2026-09-27: kit 1.5.0 and image quality

- Kit 1.5.0 synced: STANDARDS v1.5 (sections 12 to 15: product renders, storefront images and image quality, public release, authorship and signing), `.kit/cards.py`, `.kit/image_qc.py`, `.kit/release_gate.py`, issue templates, and the `/render-product` and `/release` commands. `CLAUDE.md` now matches `.kit/CLAUDE.md`.
- Every `media/render-*.png` recaptioned from its original render with the new layout: the title, concept label and repository sit in a band above the render and the view note in a band below it, each line wrapped to the image width, so no text overlaps other text or the render or runs off the image. `media/card.png` and `media/social-preview.png` regenerated with the same rules.
- `python .kit/image_qc.py` and `python .kit/release_gate.py` pass. trl stays 3.

## Session 2026-10-01: kit 1.7.0, design for construction and the prototype build plan

Kit 1.7.0 installed (`.kit/`, `.claude/commands/`, `CLAUDE.md` from `.kit/CLAUDE.md`). Following `/build-plan` and `.kit/STANDARDS.md` section 18, the model was reviewed for constructability with build123d checks, made physically buildable under Amish's 2026-09-30 instruction ("fix the design assumptions to match and be physically feasible"), and the illustrated build plan and the design decisions register were written. `design_state: constructable` is set in `project.yaml`. Nothing was built, bought or tested; TRL stays 3.

**Design changes made for construction** (TBK-DDR-003, Draft, open for Amish's review)

1. Heater wells stand on a levelled 14 mm first lift of sand at their concept height (they hung unsupported); cut length 876 mm (the BOM said 906 mm).
2. U-tubes: two elbows and a 1-1/4 x 4 in nipple (the 2-1/2 in nipple gave 118 mm leg spacing, not 155 mm), elbows resting on the drum floor; leg cut lengths 1,175 and 866 mm.
3. Lid holes 36 mm (wells, with room for the T1 to T3 sheaths) and 48 mm (legs), four 6 mm holes for T4 to T7, AES rope collars.
4. Plywood setting template on the drum rim holds the pipes during the sand fill (the concept used the lid, which blocks the fill). New BOM line 43.
5. Base: 610 mm firebrick disc (16 bricks, was 14) and AES disc, with an 89 mm stone wool batt ring out to the jacket (the concept left a void).
6. Inlet plenum 140 mm tall (was 110), collar hole cut through, flanges riveted to the cap; inlet legs 30 mm longer.
7. Collector fixed to the lid by six tabs between the wells with steel rivets; top disc with a folded, riveted edge.
8. Hot outlet passes the galvanized cap in a 180 mm hole packed with AES and covered by a black steel trim ring (the cap touched the 314 °C pipe, against R13). New BOM line 44.
9. Heaters with 72 in leads (36 in could not reach the junction box); junction box placed on the cap at 120°, 430 mm out, over a grommeted hole. New BOM line 46.
10. Thermocouples: routes through the lid, T4 bent across the sand surface to a lid hole, stainless guide rods for T4 to T7 (new BOM line 45), 1,500 mm sheaths (was 1,000 mm), one exit grommet in the cap.
11. Jacket cap from three lapped strips with a 25 mm skirt held by screws, so it lifts off for heater service (R17).

`python cad/src/model.py --check` runs 72 constructability checks; all pass.

**Key results.** Operating mass 415 kg (was 410 kg; R15 450 kg met); TBK-CAL-001 v0.3 re-run, thermal and electrical results unchanged; R3 is still **not met** (9.6 h against 8 h). Value-engineering target: USD 728. Estimated cost of the constructable design: USD 3,854 (USD 3,126 over the target; +USD 180 for construction).

**Files.** `cad/src/model.py`, `cad/src/build_plan_media.py` (new), `cad/src/sheets.py`, `cad/step/thermabrick.step`, `cad/stl/thermabrick.stl`, TBK-DWG-001 Rev P2, TBK-DWG-101 to 110 (new), `docs/05-build-plan/` (overview, 3 layouts, 9 joints, 20 steps, wiring), `docs/05-build-plan.md` TBK-BLD-001 v0.1 (new), `docs/06-design-decisions.md` TBK-DEC-001 v0.1 (new), `docs/decisions/0003-design-for-construction.md` TBK-DDR-003 v0.1 (new), TBK-CAL-001 v0.3, TBK-PRC-001 v0.6, TBK-REQ-001 v0.10, TBK-PRB-001 v0.9, `bom/bom.csv`, `bom/bom-notes.md`, `project.yaml`, `README.md`, concept media (`media/hero.png`, `cutaway.png`, `exploded.png`, `flow.png`, `concept-blueprint.*`, `model.glb`, `viewer.html`).

**Proposed, awaiting Amish** (all in TBK-DEC-001): review of the changes above; a BOM line for warning labels; keep the air path layout illustrative; plus the items carried over (standby loss, ground-fault device, render deviations).

**Stale, made on Amish's Mac.** `media/render-*.png`, `media/card.png`, `media/social-preview.png` and `cad/src/product_model.py` still show the concept base, the 110 mm plenum and no trim ring or cap fixings; the visible changes are small but real, so they should be re-rendered.

**Safety.** Unchanged in substance: the trim ring restores R13 at the outlet; the cap-edge temperature is to be confirmed at the first firing (TBK-DEC-001). The build plan carries the silica, fiber, 240 V, first-firing and stored-heat stops.

**Recommended next step.** Amish reviews TBK-DDR-003 and the register; then re-render the product images on the Mac.
