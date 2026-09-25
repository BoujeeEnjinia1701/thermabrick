# Test article build procedure

Working document for building the ThermaBrick reduced-scale test article (TBK-PRC-002), from received parts to the start of test plan TBK-TST-001. Every dimension is taken from the generated cut list, `cut-list.md`, by item number (C1 to C12). Changes to this procedure are tracked in Git.

Plan on three working days for the build, then the tests in TBK-TST-001, starting with TP0. Two people are needed to set the drum on its base. The finished unit weighs about 116 kg and is not moved once it is filled, so build it where it will be tested: indoors, on a concrete slab, with 1 m clear all round.

> **Safety:** The finished unit runs at up to 550 °C inside and on 120 V mains. Build and wire it exactly to TBK-DWG-003. Do not power the heaters until Stage L is signed off.

> **Safety:** Respirable silica and mineral fiber. Handle sand and stone wool outdoors or with local exhaust, wearing a P100 or N95 respirator, gloves, long sleeves and eye protection.

## 1. Before you start

**Documents.** Have these open or printed:

- TBK-DWG-002 (test article general arrangement);
- TBK-DWG-003 (controller schematic);
- TBK-DWG-005 (enclosure layout);
- `cut-list.md`;
- `bom/purchasing-checklist.md`, with every Received box ticked.

**Tools and safety equipment.** Those in the purchasing checklist, plus:

- a plywood disc of the drum's inner diameter to use as a template (Stage F);
- a 12 mm rod about 1 m long, for settling the sand;
- a 3 mm (1/8 in) mesh screen for sieving the sand;
- a stainless hose clamp for each of wells W1 and W3;
- steel tie wire;
- a paint pen.

**Parts added while writing this procedure.** These BOM lines came out of this procedure, so check they were bought:

- a second pack of stone wool batt, since cut list C9 needs about 5.98 m²;
- the heater cable, 16/3 SJT from the junction box to the enclosure;
- wiring consumables;
- type K extension wire with miniature connectors, which extends the 1 m probe leads to the enclosure. Keep the extension wire and connectors type K all the way to the MAX6675 terminals; a copper joint anywhere adds error.

## 2. Stage A: Incoming checks

1. Carry out every arrival check in the purchasing checklist.
2. Record each heater's cold resistance (55 Ω to 60 Ω) on the TBK-TST-001 TP0 sheet.
3. Check each type K probe with a multimeter: neither lead may be connected to the sheath (ungrounded junction). Label the probes T1 to T4 and the kit probes T5 and T6.

Type K color codes: in the US (ANSI), **yellow is positive and red is negative**. Kit probes often follow other codes, so check the polarity by warming the tip and watching the reading rise.

## 3. Stage B: Drum preparation (outdoors)

1. Remove the lid gasket and discard it. It is rated only to 121 °C.
2. Strip the exterior paint with a wire wheel or chemical stripper.
3. Burn out the rust inhibitor inside the empty drum with a small wood fire, lid off. Let it cool, then wire-brush the inside.
4. Mark the lid's +x direction (toward the controller) and its center. Drill the six holes of C3 and the three 4 mm thermocouple holes of C4. Deburr every hole.
5. Mark the sand level of C5 on the inside of the drum wall, measured from the inner floor.

## 4. Stage C: Wells and U-tube

1. Cut the four wells to the C1 length from the 3/4 in stick. Deburr the cut ends.
2. Crimp the bottom 25 mm of each well flat and closed in the vise. Fold the crimp over once more so that sand cannot enter.
3. Assemble the U-tube (C2) dry. Use no tape or sealant, which would burn out. Tighten every joint firmly so that the two legs are parallel and in one plane.
4. Trial-fit the wells and legs through the lid holes. The legs must be 206 ± 2 mm apart at the lid.

## 5. Stage D: Thermocouples on the internals

1. Clamp T1 to the outer face of well W1 with a stainless hose clamp. The tip goes at the C4 height, touching the pipe on the side facing the drum wall, with the probe running straight up the well.
2. Fit T2 to well W3 in the same way.
3. Cut two lengths of steel tie wire as guides for T3 and T4, each long enough to stand on the drum floor and reach the lid. Tie each probe to its guide so that the tip sits at the C4 height.

## 6. Stage E: Base and drum

1. Clean the slab at the final position.
2. Stand the four bricks on edge as in C6, radial at 45, 135, 225 and 315 degrees, with their centers 150 mm from the drum axis.
3. Pack stone wool between and around the bricks, to the brick height, across the full base diameter of C6.
4. With two people, set the empty drum on the bricks so that the chime bears across all four. Check it is level; shim a brick with a stone wool offcut if needed.

## 7. Stage F: Internals and sand

1. Make the template: a plywood disc of the drum's inner diameter, drilled to C3 and C4, with two 80 mm fill holes at x = ±130 mm, y = 0.
2. Stand the wells, U-tube and thermocouple guides in the drum and thread them through the template, which rests on the drum rim. Turn each well's crimp tangentially. The U-tube legs stand on the elbows, with the bend at the C2 height.
3. Sieve the sand. Weigh each bag and record the total, which should be 68 kg.
4. Pour the sand through the fill holes in lifts of about 100 mm. Settle each lift by pushing the rod down all over the surface, working around every pipe and probe. Keep the probes on their marks.
5. Stop at the C5 level mark. Record the mass poured and the measured depth.
6. Lift the template off over the pipes.

## 8. Stage G: Heaters

1. Lower a heater into each well, lead end up, until it rests on the crimp.
2. Run the leads straight up out of the well. They must not bend sharply where they leave the well mouth.

## 9. Stage H: Insulation and jacket

1. **Headspace (C7).** Lay the two stone wool discs on the sand, threading the wells, legs, heater leads and probes through their holes.
2. **Lid.** Lay a strip of stone wool around the rim as the gasket. Fit the lid over the pipes, probes and leads, then fit and bolt the closing ring. Pack stone wool into any gap around each pipe where it passes through the lid.
3. **Side (C8).** Wrap the three layers, staggering the joints between layers. Hold each layer with steel tie wire.
4. **Top (C9).** Lay the two discs over the lid, slit to pass the legs, leads and probes.
5. **Jacket (C10).** Wrap the two side rows with a 50 mm overlap. Fix the vertical seams with sheet metal screws and seal them with foil tape.
6. **Top cap.** Cut the cap with the leg holes and cable exits, and fit it over the top.
7. **Junction box.** Rivet the heater junction box to the top cap through a scrap reinforcing plate at least 100 mm square, 50 mm or more from either leg. Land the eight heater leads on the ceramic terminal block: all four first leads on one side (L_HEAT), all four second leads on the other (N).
8. **Cable.** Bring the heater cable into the box. Bond its green (PE) conductor to the drum with a ring lug under a closing-ring bolt.

## 10. Stage I: Blower and stack

1. Tape the blower outlet to the top of the inlet leg with aluminum foil tape, sealing all round.
2. Hang the stovepipe over the outlet leg so that the leg ends 40 mm inside its open bottom (C2). Hold it with three tie wires to the leg.
3. Fit T5 50 mm down inside the outlet leg top, and hang T6 300 mm from the blower intake, shaded from the unit.

> **Safety:** Keep 450 mm clear of combustibles around the stack, and guard it from casual contact.

## 11. Stage J: Controller enclosure

1. **Cutouts.** Mark and cut the lid and gland holes of C11. Cut the REX-C100 square by drilling the corners and joining them with a jigsaw or nibbler, then file to 45 mm. Fit the glands and buttons.
2. **Mounting plate.** Lay out the plate to TBK-DWG-005: the DIN rail at the C11 height with PS1 and the K1 socket on it, the SSR on its heat sink at top right (with thermal pad, fins vertical), and the controller area at bottom left. Fit the earth stud, and bond the plate to it.
3. **Controller.** Mount the ESP32, buck converter, MOSFET module, R1 and R2 and the five MAX6675 modules on perfboard in the controller area. Alternatively, fit the optional board (TBK-DWG-004).
4. **Mains wiring.** Wire every net in the C12 wiring list, starting with the mains nets:
   - the cord (14 AWG) goes to the fuse holder, and all other mains wiring is 16 AWG;
   - make the L_F and N junctions with the lever connectors under the REX-C100 position;
   - bond PE from the cord, plate, heater cable and enclosure to the earth stud.
5. **Low-voltage wiring.** Wire the low-voltage nets in 22 AWG, following `firmware/README.md`, Table 1. Fit the 10 kΩ pull-downs R1 and R2 at the ESP32 end.
6. **Thermocouples.** Join each probe lead to type K extension wire with a miniature type K plug and jack, and bring it in through the M25 gland. Land T1 and T3 to T6 on their MAX6675 modules, and T2 on the REX-C100 input, observing polarity.
7. **Lid.** Fit the REX-C100 and the buttons to the lid. Leave enough slack in their wires for the lid to open fully.

## 12. Stage K: Checks with the unit unplugged

| Check | Between | Expect |
| --- | --- | --- |
| Earth continuity | Plug earth pin to drum, jacket, stack, plate, enclosure stud, junction box and SSR heat sink | 0.5 Ω or less each |
| Heater load | SSR terminal 2 (L_HEAT) to N at the enclosure | 14 Ω to 15 Ω (four heaters in parallel, cold) |
| Heater insulation | L_HEAT and N to earth | Open on the multimeter's highest range |
| Mains short | Plug L to N, with START not pressed | Open, or the PS1 input only (not a short) |
| Coil path | Plug L to K1 coil A1 | Open (the REX-C100 relay is open while unpowered) |
| 12 V rail | +12V to GND | Not shorted |
| SSR input | GPIO 26 side of the SSR input to GND | About 10 kΩ (R1) |

*Table 1. Checks before power.*

## 13. Stage L: First power-up, heaters disconnected

1. Disconnect the heater cable's L_HEAT conductor from SSR terminal 2 and insulate it.
2. Press TEST on the GFCI receptacle to confirm it trips, reset it, and plug in the unit.
3. Check that PS1's LED lights and the 12 V rail reads 11.5 V to 12.5 V. Set the buck converter to 5.0 V before connecting the ESP32.
4. Configure the REX-C100 for on-off heating action with its relay output, setpoint 600 °C and type K input. Follow the supplier's manual. At room temperature its relay must be closed.
5. Press START: K1 pulls in and holds. Press STOP: K1 drops. Press START again, then unplug and replug the unit: K1 must stay open until START is pressed.
6. Build and flash the firmware (`firmware/README.md`), then set `v_line` to the measured line voltage. Set `r_heat` to the parallel resistance measured in Stage K multiplied by 1.04.
7. Start the logger. Check that T1 and T3 to T6 all read room temperature within ±2 K, and that T2 on the REX-C100 agrees. Warm each probe by hand to confirm it is the right channel.
8. Run the blower at 50 % from `/blower?mode=duty&value=0.5`; air must blow out of the stack. Turn it off.
9. Unplug the unit, reconnect L_HEAT to SSR terminal 2, and close the enclosure.

The build is complete. Start TBK-TST-001 at TP0, then run TP1 (limit test, cold) before any heating.

## 14. Sign-off

| Stage | Done by | Date | Notes |
| --- | --- | --- | --- |
| A Incoming checks | | | |
| B Drum preparation | | | |
| C Wells and U-tube | | | |
| D Thermocouples | | | |
| E Base and drum | | | |
| F Internals and sand (record mass and depth) | | | |
| G Heaters | | | |
| H Insulation and jacket | | | |
| I Blower and stack | | | |
| J Controller enclosure | | | |
| K Checks unplugged | | | |
| L First power-up | | | |

*Table 2. Build sign-off.*
