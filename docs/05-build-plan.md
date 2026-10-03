---
doc_id: TBK-BLD-001
title: ThermaBrick prototype build plan
project: ThermaBrick
doc_type: Build plan
version: "0.2"
status: Draft
date: '2026-10-02'
author: Amish Chadha
license: CERN-OHL-S-2.0
revisions:
  - version: "0.1"
    date: '2026-10-01'
    author: Amish Chadha
    change: First build plan, with pictures by component and step; design made constructable (TBK-DDR-003)
  - version: "0.2"
    date: '2026-10-02'
    author: Amish Chadha
    change: Step 22 and Figure 26 added for the five warning labels (BOM line 47); label line in the bought components
---

# ThermaBrick prototype build plan

**Plan, not yet built.** How to build the first full-scale proof-of-concept ThermaBrick, component by component. Building and testing to it is TRL 4 work, which is on hold. Decisions still to be made are kept in the design decisions register ([docs/06-design-decisions.md](06-design-decisions.md)), not here.

## 1. What you are building

![Figure 1. Every component, pulled apart and numbered in build order](05-build-plan/overview.png)

*Figure 1. Every component pulled apart and numbered in build order, in four columns: the base; the drum and the pipes that stand in it; what goes into and onto the drum; the jacket and what sits on top. The setting template (9) is a temporary jig.*

ThermaBrick is a 55 US gal steel drum filled with 210 kg of dry sand, with twelve electric heaters in capped steel pipes (the wells) to charge it and six steel U-tubes to carry room air through it and take the heat out. The drum stands on an insulated base and is wrapped in 317 mm of fiber insulation inside a galvanized steel jacket, 1,209 mm across and 1,462 mm high. Figure 1 shows the 21 components in the order you make or fit them. Ten are made in a home workshop: the base layers, the drilled drum lid, a plywood setting template, the wells, the U-tubes, the collector and outlet, the jacket side and cap, a steel trim ring and the inlet plenum. Everything else is bought: sand, heaters, thermocouples, insulation, the air path parts and the controls. The work is cutting and threading black steel pipe, drilling sheet steel with hole saws, cutting firebrick and fiber insulation, and cutting, folding and riveting thin sheet metal. No welding, machining or pressure parts. The parts cost about USD 3,870 from the bill of materials. The finished unit weighs about 415 kg and must stand on a concrete slab.

> **Safety:** The bed runs at up to 550 °C at the heater wells and stays hot for days after the power is off. The heaters run on 240 V: the branch circuit and the control enclosure are wired or checked by a licensed electrician. Pouring sand and cutting firebrick release respirable crystalline silica, and fiber insulation irritates skin, eyes and airways: work outdoors or with local exhaust, and wear a P100 or N95 respirator, gloves, long sleeves and eye protection. The first firing gives off smoke from coatings and the insulation binder. Section 6 lists every stop point.

## 2. What changed to make it buildable

The concept showed what ThermaBrick does and sized it; some of its parts could not be made, fixed or assembled as drawn. Each change below keeps what the unit does, and all of them are recorded in decision record TBK-DDR-003, open for Amish's review.

*Table 1. Changes from the concept.*

| Component | The concept had | The buildable design has | Why |
| --- | --- | --- | --- |
| Heater wells | Wells hanging 14 mm above the drum floor with nothing under them | Each well stands on a levelled 14 mm first layer of sand, at the same height (Figure 9) | Supports the wells without putting hot steel against the drum floor |
| U-tube bottoms | Floating 50 mm above the floor; the listed 2-1/2 in nipple set the legs 118 mm apart, not 155 mm | Two elbows and a 4 in nipple, resting on the floor (Figure 11) | The stock fittings now give the 155 mm leg spacing, and the tube has a firm seat |
| Lid holes | 1 mm clear of each pipe; no way through for the thermocouples | 36 mm holes for the wells, 48 mm for the U-tube legs, 6 mm for four sand thermocouples, a fiber rope collar round each pipe (Figures 5, 6) | The lid can be lowered over 24 pipes at once; the well-wall thermocouples pass beside their wells |
| Holding the pipes during the fill | The lid on spacers, which leaves no way to pour the sand | A plywood setting template on the drum rim, with five pour holes (Figure 7) | Holds every pipe upright until the sand locks it |
| Base | One solid layer; firebrick only under the drum, leaving a gap out to the jacket | A 610 mm firebrick disc and AES board disc, with a ring of stone wool batt round them (Figures 2, 3, 4) | A level, fully filled base; the firebrick still carries the drum |
| Inlet plenum | 110 mm tall, 4 mm of wall round the 4 in collar, no fixing | 140 mm tall, collar hole cut through, flanges riveted to the cap (Figures 23, 24) | Room to rivet the collar; a fixing for the plenum |
| Collector | No fixing to the lid | Six tabs folded out between the wells and riveted to the lid (Figures 13, 14) | A fixing that clears the wells |
| Outlet through the jacket | Galvanized cap touching the hot outlet | A 180 mm hole packed with fiber and covered by a black steel trim ring (Figures 21, 22) | Keeps zinc away from the hot pipe, as requirement R13 asks |
| Heater leads and junction box | 36 in leads, too short for most wells; no position for the box | 72 in leads; the box on the cap at 120°, 430 mm out (Figures 19, 20) | Every lead reaches the box |
| Thermocouples | No route out of the drum; 1,000 mm sheaths too short | Routes through the lid, guide rods for the sand sensors, 1,500 mm sheaths, one exit in the cap (Figures 6, 12) | Every sensor reaches the outside at its stated measuring point |
| Jacket cap | No fixing; drawn as one sheet wider than the flashing | Three lapped strips with a turned-down skirt, held by screws (Figures 16, 18) | The cap can be lifted off to change a heater |

## 3. Making the components

Make and check each component before the assembly step that needs it. Sizes are in millimetres. Angles are measured anticlockwise, seen from above, from a 0° mark on the drum rim (the side where the inlet plenum's collar will point). Workshop tolerance is 2 mm unless a step says otherwise; drawings do not carry tolerances before TRL 4.

### 3.1 Base

![Figure 2. Making sketch of the base](../cad/drawings/TBK-DWG-101.png)

*Figure 2. Base making sketch (TBK-DWG-101).*

![Figure 3. Firebrick disc cutting layout](05-build-plan/brick-layout.png)

*Figure 3. Firebrick disc cutting layout: 19 pieces cut from 15 bricks.*

**What it is and what it is made from.** Four layers, 189 mm thick in all, that carry the drum and keep its heat out of the floor. Two layers of 50 mm stone wool board (four boards of 610 x 1,219 mm); one course of K-23 insulating firebrick laid flat (16 bricks of 230 x 114 x 64 mm); one 25 mm AES fiber board (610 x 914 mm); and a ring of 89 mm stone wool batt.

**How to make it.**

1. Butt two stone wool boards into a 1,219 mm square, draw a 1,208 mm circle with a trammel and cut it with a long serrated knife. Repeat for the second layer.
2. Lay the bricks dry in staggered rows as Figure 3 shows, with 2 mm joints. Mark a 610 mm circle and number the pieces.
3. Cut the bricks outdoors with a coarse handsaw or a masonry blade, wearing a respirator. Use the offcuts for the small edge pieces marked with the same number.
4. Cut a 610 mm disc from the AES board.
5. Cut the 89 mm batt into segments that fill the ring from 610 mm to 1,208 mm across.

**How it fits the parts next to it.**

![Figure 4. Joint 1: the drum on the base](05-build-plan/joint-01.png)

*Figure 4. The drum's bottom rim stands on the AES disc, 6 mm in from its edge, over the firebrick; the batt ring fills out to the jacket, level with the AES disc.*

The two board layers lie on the slab with their joints crossed. The firebrick disc sits in the middle of the top board, the AES disc on the bricks, and the batt ring round both, all level at 189 mm. The drum's 597 mm bottom rim stands on the AES disc; the firebrick under it carries the full 415 kg.

**Check before moving on.** A straight edge across the top shows no gap over 3 mm; the AES disc does not rock.

### 3.2 Drum and drum lid

![Figure 5. Drilling sketch of the drum lid](../cad/drawings/TBK-DWG-102.png)

*Figure 5. Drum lid drilling sketch (TBK-DWG-102).*

![Figure 6. Lid and template hole layout](05-build-plan/lid-layout.png)

*Figure 6. Lid and template hole layout, with the thermocouple positions T1 to T7.*

**What it is and what it is made from.** A new, unlined, open-head 55 US gal steel drum (571.5 mm inside, 883 mm high, 18 ga body) with its 16 ga lid and bolted closing ring. The lid carries 28 holes.

**How to make it.**

1. Strip the outside paint with a flap disc. Burn the empty drum outdoors to about 300 °C (a wood fire round it) to remove residues; let it cool and brush it out.
2. Mark a 0° line on the drum rim and on the lid edge.
3. Make the setting template first (section 3.3), clamp it on the lid with the 0° marks together, and drill through it.
4. Twelve 36 mm holes for the wells: six on a 150 mm radius and six on 245 mm, both at 0, 60, 120, 180, 240 and 300°.
5. Twelve 48 mm holes for the U-tube legs: six on 80 mm and six on 235 mm, at 30, 90, 150, 210, 270 and 330°.
6. Four 6 mm holes for the sand thermocouples: T4 at 165 mm and 51°, T5 at 200 mm and 45°, T6 at 270 mm and 45°, T7 at 200 mm and 225°.
7. Use bi-metal hole saws at low speed with cutting oil; deburr and degrease.

**How it fits the parts next to it.** The lid drops over all 24 pipe ends at once: each well hole leaves 4.6 mm round the well, enough for the well-wall thermocouple beside it, and each leg hole 2.9 mm. A collar of 12 mm AES rope is laid round every pipe on top of the lid, and the closing ring is bolted as the drum maker supplies it. The bed breathes through the collars; nothing is sealed or pressurized.

**Check before moving on.** The template laid on the lid lines up with every hole.

### 3.3 Setting template

![Figure 7. Making sketch of the setting template](../cad/drawings/TBK-DWG-103.png)

*Figure 7. Setting template making sketch (TBK-DWG-103).*

**What it is and what it is made from.** A temporary plywood disc that sits on the drum rim and holds every pipe and sensor upright while the sand is poured. Exterior plywood 18 mm, 610 x 610 mm.

**How to make it.**

1. Cut a 597 mm disc. Mark the centre and the 0° line.
2. Drill the 28 holes of Figure 6 with the same hole saws as the lid.
3. Cut the pour holes: 80 mm in the centre and four of 64 mm on a 200 mm radius at 15, 105, 195 and 285°.
4. Sand the edges so it lifts off without snagging.

**How it fits the parts next to it.** It lies on the drum's top rim where the lid will go, 0° marks together, clamped at four points. Every pour hole is at least 10 mm from a pipe hole.

**Check before moving on.** It lies flat on the rim.

### 3.4 Heater wells (make 12)

![Figure 8. Making sketch of the heater well](../cad/drawings/TBK-DWG-104.png)

*Figure 8. Heater well making sketch (TBK-DWG-104).*

**What it is and what it is made from.** A capped steel pipe that a cartridge heater slides into, so the heater never touches the sand and can be pulled out from above. Black (uncoated) steel pipe 3/4 in Sch 40 (26.7 mm outside), four 10 ft lengths; twelve 3/4 in malleable iron caps.

**How to make it.**

1. Cut twelve lengths of 876 mm, three from each pipe. Square the ends.
2. Thread one end of each 3/4 in NPT with a rented pipe threader; ream and deburr both ends.
3. Degrease inside and out: cutting oil smokes on the first firing.
4. Coat the thread with nickel anti-seize (never PTFE tape or paste) and screw on a cap, hand tight plus one and a half turns.

**How it fits the parts next to it.**

![Figure 9. Joint 2: heater well foot](05-build-plan/joint-02.png)

*Figure 9. The cap stands on a levelled 14 mm first layer of sand, which keeps it off the drum floor; the heater rests in the cap.*

Each well stands on its cap at its mark, held upright by the template and then the lid; its open top ends 25 mm above the lid. The heater rests on the inside of the cap, its heated length from 26 to 483 mm above the drum floor, and its leads rise out of the open top.

**Check before moving on.** A 16 mm rod slides to the bottom of every well freely.

### 3.5 U-tubes (make 6)

![Figure 10. Making sketch of the U-tube](../cad/drawings/TBK-DWG-105.png)

*Figure 10. U-tube making sketch (TBK-DWG-105).*

**What it is and what it is made from.** The heat exchanger: room air goes down the long leg, across the bottom and up the short leg, picking up heat from the sand without ever touching it. Black steel pipe 1-1/4 in Sch 40 (42.2 mm outside), five 10 ft lengths; twelve 1-1/4 in malleable iron 90° elbows; six 1-1/4 x 4 in black nipples.

**How to make it.**

1. Cut six long (inlet) legs of 1,175 mm, two from each of three pipes, and six short (outlet) legs of 866 mm, three from each of two pipes.
2. Thread one end of each; ream, deburr and degrease.
3. Coat every thread with nickel anti-seize and join, wrench tight: short leg, elbow, 4 in nipple, elbow, long leg.
4. Turn the second elbow so the two legs are parallel and in one plane, 155 mm apart between centres.
5. Blow through each tube to clear swarf.

**How it fits the parts next to it.**

![Figure 11. Joint 3: U-tube foot](05-build-plan/joint-03.png)

*Figure 11. Two elbows and a 4 in nipple set the legs 155 mm apart; the elbows rest on the drum floor.*

The elbows rest on the drum floor, the bottom run 28 mm above it. The short leg stands on the 80 mm circle and ends 50 mm above the lid, inside the collector; the long leg stands on the 235 mm circle and ends inside the inlet plenum, 130 mm above the jacket cap.

**Check before moving on.** The legs are parallel within 3 mm over their length.

### 3.6 Thermocouples and guide rods

![Figure 12. Joint 9: sand thermocouple on its guide rod](05-build-plan/joint-09.png)

*Figure 12. Each sand thermocouple is tied to a stainless rod that stands on the drum floor.*

**What it is and what it is made from.** Eight type K mineral-insulated thermocouples, 3 mm Inconel sheath, 1,500 mm long, with mini plugs; four stainless rods 4.8 mm, cut to 561 mm; stainless tie wire.

**How to fit them.** Their positions are in Figure 6.

1. Well walls: T1 on the inner-ring well at 0°, T2 on the outer-ring well at 180° (on its inner side), T3 on the inner-ring well at 120°. Tie each sheath to its well with stainless wire, its tip 255 mm above the drum floor (the middle of the heated length).
2. Sand: stand a guide rod on the floor 7 mm inboard of each sand position and tie the sheath to it every 100 mm. T5 (200 mm, 45°) and T6 (270 mm, 45°) with tips 286 mm above the floor; T7 (200 mm, 225°) with its tip 471 mm above the floor.
3. T4 measures the centre: its rod stands 7 mm off the centre, its tip 286 mm above the floor. Above the sand, bend its sheath once by hand and run it across the sand surface at 51°, between two short U-tube legs, to its lid hole at 165 mm.
4. T8 goes in later, through the 4 mm hole in the collector top, into the collector air.
5. Above the lid, every sheath runs in the top insulation to the exit grommet in the cap; coil the spare length flat in the insulation.

**Check before moving on.** Each thermocouple reads room temperature on a meter, and its tip is at its stated height within 10 mm.

### 3.7 Collector and outlet

![Figure 13. Making sketch of the collector](../cad/drawings/TBK-DWG-106.png)

*Figure 13. Collector and outlet making sketch (TBK-DWG-106).*

**What it is and what it is made from.** A shallow drum on the lid that gathers the hot air from the six short legs and sends it up the 4 in outlet. A section of 10 in (254 mm) black stovepipe, 24 ga; 18 ga uncoated steel sheet; a 4 in crimped start collar and 4 in black steel pipe; steel pop rivets.

**How to make it.**

1. Cut an 80 mm band from the stovepipe and close its seam.
2. At the foot, at 30, 90, 150, 210, 270 and 330°, make two 20 mm slits 20 mm apart and fold each tab out flat. Drill each tab 4.9 mm, 10 mm out from the ring.
3. Cut a 266 mm disc of 18 ga sheet; fold a 12 mm edge down and rivet it over the ring in six places.
4. Cut a 4 in hole in the middle of the disc and rivet in the start collar. Drill a 4 mm hole 95 mm from the centre for T8.
5. Fit the 4 in pipe in the collar, long enough to stand 160 mm above the jacket cap (about 300 mm).

**How it fits the parts next to it.**

![Figure 14. Joint 5: collector tab on the lid](05-build-plan/joint-05.png)

*Figure 14. Each tab lies on the lid between two inner-ring wells and is held by one steel rivet.*

The ring stands on the lid over the six short legs, 9.6 mm clear of the inner wells. Each tab is riveted to the lid with a steel rivet (never aluminium in the hot zone), and AES rope is pressed round the foot of the ring.

**Check before moving on.** The collector sits flat; no tab touches a well.

### 3.8 Jacket side

![Figure 15. Making sketch of the jacket side](../cad/drawings/TBK-DWG-107.png)

*Figure 15. Jacket side making sketch (TBK-DWG-107).*

**What it is and what it is made from.** The outer skin, 1,210 mm across and 1,302 mm high, that holds the side insulation. Galvanized steel flashing 0.6 mm, 610 mm wide coil; aluminium pop rivets.

**How to make it.**

1. Cut three strips 3,850 mm long (3,800 mm round plus a 50 mm lap). Cut the top strip to the width that brings the side to 1,302 mm with 25 mm laps between rows.
2. Wrap the bottom strip round the insulated unit on the floor, pull it tight with two ratchet straps, and rivet the vertical lap every 100 mm.
3. Add the second and top rows, each lapping 25 mm outside the one below, the vertical laps staggered. Rivet the row laps every 150 mm.

**How it fits the parts next to it.** The jacket stands on the slab round the base and holds the 317 mm of side insulation. The cap's skirt sits outside its top edge (Figure 18). The jacket runs at about 26 °C, so galvanized steel is allowed here.

**Check before moving on.** Two diameters at right angles agree within 10 mm; no gap at any lap.

### 3.9 Jacket cap

![Figure 16. Making sketch of the jacket cap](../cad/drawings/TBK-DWG-108.png)

*Figure 16. Jacket cap making sketch (TBK-DWG-108).*

![Figure 17. Jacket cap hole layout](05-build-plan/cap-layout.png)

*Figure 17. Jacket cap hole layout and the outlines of the parts that sit on it.*

**What it is and what it is made from.** The removable top of the jacket. Three strips of the same flashing, stainless sheet metal screws, two silicone grommets.

**How to make it.**

1. Cut three strips 1,260 mm long, lap them 25 mm and rivet the laps every 100 mm. Cut a 1,260 mm disc.
2. Snip the edge every 50 mm, 25 mm deep, and turn it down 90° to make the skirt.
3. Cut the holes of Figure 17: 180 mm in the centre for the outlet; six of 46 mm on a 235 mm radius at 30, 90, 150, 210, 270 and 330° for the long legs; 40 mm at 120°, 430 mm out, under the junction box; 25 mm at 95°, 330 mm out, for the thermocouple exit.
4. Fit grommets in the 40 mm and 25 mm holes.

**How it fits the parts next to it.** It lowers over the six long legs and the outlet and rests on the top insulation; the heater leads and thermocouple sheaths come up through the grommets. Eight sheet metal screws through the skirt hold it to the jacket side, so it can be lifted off to reach a heater.

![Figure 18. The jacket cap going on (assembly step 16)](05-build-plan/step-16.png)

*Figure 18. The cap lowers over the six long legs and the outlet; its skirt sits outside the top row of the jacket side.*

**Check before moving on.** Every hole lines up with its pipe before the cap is pressed down.

### 3.10 Heater junction box

![Figure 19. Joint 8: junction box on the cap](05-build-plan/joint-08.png)

*Figure 19. The heater leads rise through the top insulation and the grommet into the box.*

**What it is.** A bought steel box, 150 x 150 x 100 mm, with ceramic terminal blocks, where the 24 heater leads meet the cable from the control enclosure.

**What to do to it.** Drill a 40 mm hole in its floor to match the cap hole, and four 4.5 mm holes for screws. Fit a cable gland for the supply cable. It sits on the cap at 120°, 430 mm out, 60 mm clear of the plenum.

![Figure 20. Step 19: junction box](05-build-plan/step-19.png)

*Figure 20. The box goes on last, over the leads (assembly step 19).*

### 3.11 Outlet trim ring

![Figure 21. Making sketch of the outlet trim ring](../cad/drawings/TBK-DWG-109.png)

*Figure 21. Outlet trim ring making sketch (TBK-DWG-109).*

**What it is and what it is made from.** A flat steel ring that covers the fiber packing where the hot outlet passes through the cap. 18 ga (1.2 mm) uncoated steel sheet.

**How to make it.**

1. Cut a 250 mm disc with snips and file the edge.
2. Cut a 106 mm hole in the middle.
3. Drill four 3.5 mm holes on a 230 mm circle.

**How it fits the parts next to it.**

![Figure 22. Joint 6: hot outlet through the jacket cap](05-build-plan/joint-06.png)

*Figure 22. The galvanized cap stops 39 mm from the hot pipe; fiber packing fills the gap and the trim ring covers it.*

The 39 mm gap between the outlet and the cap is packed 20 mm deep with AES blanket. The ring lies on the packing and the cap, 2.3 mm clear of the pipe all round, held by four screws at its outer edge.

**Check before moving on.** The ring touches the pipe nowhere.

### 3.12 Inlet plenum

![Figure 23. Making sketch of the inlet plenum](../cad/drawings/TBK-DWG-110.png)

*Figure 23. Inlet plenum making sketch (TBK-DWG-110).*

**What it is and what it is made from.** A ring-shaped sheet metal box on the cap that takes room air from the 4 in inlet collar and shares it among the six long legs. Galvanized flashing 0.6 mm; a 4 in crimped start collar; pop rivets; foil tape.

**How to make it.**

1. Cut two strips 170 mm wide: 1,780 mm long for the outer wall and 1,220 mm for the inner wall. Roll each into a ring (560 mm and 380 mm across) and rivet a 25 mm lap.
2. Cut the top: a ring 560 mm outside and 380 mm inside.
3. On each wall, snip the top 15 mm every 40 mm, fold the tabs over the top and rivet them.
4. Snip the bottom 15 mm every 40 mm and fold the tabs out (outer wall) or in (inner wall) as flanges.
5. In the outer wall at 0°, cut a 4 in hole centred 70 mm up and rivet in the start collar, which leaves 19 mm of wall above and below it.

**How it fits the parts next to it.**

![Figure 24. Joint 7: inlet leg into the plenum](05-build-plan/joint-07.png)

*Figure 24. A long leg passes through the cap and ends 10 mm below the plenum top.*

The plenum sits over the six long legs with its flanges on the cap, riveted and sealed with foil tape. The inlet damper fits on the collar.

**Check before moving on.** Air blown into the collar comes out of the outlet; none escapes at the flanges.

### 3.13 Wiring

![Figure 25. Block-level wiring and the safety chain](05-build-plan/wiring.png)

*Figure 25. Block-level wiring. The 240 V circuit and the control enclosure are wired or checked by a licensed electrician.*

The heaters are wired as two groups of six (1.5 kW each), each through a 10 A fuse pair and a solid-state relay, with a 2-pole safety contactor ahead of both groups. The contactor's 24 V coil runs through the independent high limit on thermocouple T3, which opens it at 600 °C and latches until reset by hand. The ESP32 controller reads T1, T2 and T4 to T8, the air and surface sensors and the export meter, and drives the relays, the damper servo and the fan speed. Wire to the bill of materials: 12 AWG to the enclosure on a dedicated 20 A circuit with 2-pole ground-fault protection; high-temperature 14 AWG from the enclosure to the junction box; type K extension cable from the exit grommet to the amplifiers.

### 3.14 Bought components

Buy to specification, not brand. Line numbers are those of the bill of materials.

- **Drum (line 1).** New, unlined, open-head 55 US gal steel drum, 18 ga body, 16 ga lid with bolted ring, 571.5 mm inside.
- **Sand (line 2).** Ten 50 lb (22.7 kg) bags of washed play sand, sieved to remove fines.
- **Heaters (line 3).** Twelve cartridge heaters 5/8 x 20 in (15.9 x 508 mm), 250 W at 240 V, Incoloy 800 sheath, 2 in cold end, **72 in (1,829 mm) ceramic-beaded leads**.
- **Pipe and fittings (lines 4 to 9).** As sections 3.4 and 3.5, with nickel anti-seize.
- **Collector parts (lines 10, 11).** As section 3.7.
- **Air path (lines 12 to 18).** 4 in black stovepipe kit with two adjustable elbows, 4 in tee, 4 in galvanized butterfly damper with a hobby servo, 4 in balancing damper, 4 in EC inline fan (60 L/s at 150 Pa, speed input, rated for 60 °C air), insulated flexible duct and a register.
- **Insulation (lines 19 to 24).** Two rolls of 25 mm AES blanket, one AES board, 16 firebricks, three packs of 89 mm stone wool batt, four 50 mm stone wool boards (60 kPa or more at 10 % strain), two 3 m lengths of 12 mm AES rope.
- **Jacket (lines 25, 26).** Two coils of 610 mm galvanized flashing; aluminium and steel pop rivets, stainless sheet metal screws, foil tape.
- **Controls (lines 27 to 42).** As Figure 25 and the bill of materials.
- **New for construction (lines 43 to 46).** Plywood for the template, 18 ga uncoated steel for the trim ring, four stainless guide rods, silicone grommets.
- **Warning labels (line 47).** Five self-adhesive vinyl labels rated 105 °C or higher; positions in step 22.

## 4. Putting it together

In each picture the parts already fitted are grey and the part being fitted is in colour, with an arrow showing the way it goes in. The drum is drawn with a quarter cut away where the inside matters.

### Step 1: stone wool boards on the slab

![Step 1](05-build-plan/step-01.png)

On a clean, level concrete slab inside the heated space, at least 450 mm from anything combustible. Two layers, joints crossed.

### Step 2: firebrick disc, AES disc and batt ring

![Step 2](05-build-plan/step-02.png)

Bricks to the cutting layout, dry, in the middle; the AES disc on top; the batt ring round both, level with the AES disc.

### Step 3: drum onto the base

![Step 3](05-build-plan/step-03.png)

Empty and prepared, centred on the AES disc (two people lift it), with its 0° mark facing where the inlet duct will come from. It is not moved again.

### Step 4: heater wells into the drum

![Step 4](05-build-plan/step-04.png)

Pour and level a 14 mm first layer of sand with a short board. Stand each capped well on it at its mark from Figure 6. Tape over the open tops so no sand gets in.

### Step 5: U-tubes into the drum

![Step 5](05-build-plan/step-05.png)

Elbows on the floor (scrape the sand clear under them), short legs on the 80 mm circle, long legs on the 235 mm circle, each tube on its ray at 30, 90, 150 ... °. Tape the tops.

### Step 6: thermocouples and guide rods

![Step 6](05-build-plan/step-06.png)

As section 3.6: T1 to T3 wired to their wells, guide rods for T4 to T7 standing on the floor with the sheaths tied to them.

### Step 7: setting template onto the rim

![Step 7](05-build-plan/step-07.png)

Lower it over every pipe and sheath end, 0° marks together, and clamp it at four points. **Hold point:** every pipe stands upright in its hole; the template lies flat.

### Step 8: fill with sand

![Step 8](05-build-plan/step-08.png)

Dust control as safety stop S1: outdoors or local exhaust, and a respirator. Pour through the pour holes in 100 mm layers to 571 mm above the floor, rodding each layer round the pipes. Weigh every bag: 210 kg in all. Check the pipes stay upright as you go.

### Step 9: template off, headspace insulation in

![Step 9](05-build-plan/step-09.png)

Lift the template off. Lay 50 mm of AES blanket on the sand, then stone wool batt to the rim, cut round every pipe and sheath. Bend T4 across the sand surface first (section 3.6).

### Step 10: lid and closing ring

![Step 10](05-build-plan/step-10.png)

0° marks lined up; lower the lid over all 24 pipe ends and the four sand sheaths, passing T1 to T3 through their well holes. Lay an AES rope collar round each pipe and bolt the closing ring.

### Step 11: collector and outlet onto the lid

![Step 11](05-build-plan/step-11.png)

Over the six short legs, tabs between the wells; one steel rivet through each tab into the lid; AES rope round the foot of the ring. Fit T8 through the collector top.

### Step 12: heaters into the wells

![Step 12](05-build-plan/step-12.png)

Remove the tape. Lower each heater on its leads until it rests on the cap. Lay the leads across the lid toward the junction box position (120°), labelled by well. **Hold point:** each heater reads 1 MΩ or more at 500 V to its sheath before the top insulation covers it.

### Step 13: side insulation

![Step 13](05-build-plan/step-13.png)

Two layers of 25 mm AES blanket against the drum, then three layers of 89 mm stone wool batt, joints staggered, held with wire until the jacket closes.

### Step 14: jacket side

![Step 14](05-build-plan/step-14.png)

Three rows, strapped tight and riveted as section 3.8.

### Step 15: top insulation

![Step 15](05-build-plan/step-15.png)

50 mm of AES blanket over the lid and collector, then stone wool batt to the top of the jacket, cut round the outlet and the long legs. Bring the heater leads up at the junction box position and the sheaths at the exit position; coil the spare sheath in the batt.

### Step 16: jacket cap

![Step 16](05-build-plan/step-16.png)

Lower it over the long legs and the outlet, threading the leads and sheaths through their grommets. Eight screws through the skirt. Foil tape round each long leg.

### Step 17: outlet packing and trim ring

![Step 17](05-build-plan/step-17.png)

Pack the 39 mm gap round the outlet with AES blanket, 20 mm deep. Lay the black steel ring over it and screw it to the cap.

### Step 18: inlet plenum

![Step 18](05-build-plan/step-18.png)

Over the six long legs, collar at 0°; rivet the flanges to the cap and seal them with foil tape.

### Step 19: heater junction box

![Step 19](05-build-plan/step-19.png)

Over the 40 mm grommet; four screws to the cap. Land the leads on the ceramic terminal blocks in two groups of six, as Figure 25.

### Step 20: air path: damper, outlet duct, tee and fan

![Step 20](05-build-plan/step-20.png)

The damper and its servo on the inlet collar. The 4 in outlet rises, turns and drops to the mixing tee as a heat trap; guard it with a perforated steel sleeve and keep it 450 mm from anything combustible. The balancing damper on the tee's room-air branch, then the fan below the tee, then the flexible duct to the register. The layout shown is one site; the rules are what matter.

### Step 21: control enclosure and wiring

The picture for this step is Figure 25. The control enclosure goes on the wall beside the unit. A licensed electrician runs the dedicated 240 V circuit and checks the wiring of Figure 25. **Hold point:** safety stop S5.

### Step 22: warning labels

![Figure 26. Step 22: warning label positions](05-build-plan/step-22.png)

*Figure 26. The five warning labels and where they go (assembly step 22).*

Stick the labels on clean, dry metal once the unit is finished and the air path is in place, in this order:

1. HOT SURFACES INSIDE on the jacket side, at the front (0°), 1,060 mm above the floor.
2. HOT OUTLET on the jacket cap, 470 mm from the centre at 205°, clear of the plenum and the trim ring.
3. DANGER 240 V on the outer face of the junction box.
4. HOT SURFACE on the drop of the guard sleeve, facing the room.
5. DANGER 240 V on the door of the control enclosure.

**Check before moving on.** All five labels are on, square and readable from a standing position.

## 5. First checks

These are the checks a TRL 4 test report would record; this plan only lists them. Requirement numbers are those of TBK-REQ-001.

*Table 2. First checks.*

| Check | Requirement | How | Pass when |
| --- | --- | --- | --- |
| Envelope | R14 | Tape and level | 1,250 mm across or less; 1,500 mm high or less with the outlet stub |
| Heater insulation | R11 | 500 V insulation tester, each heater lead to sheath, before and after the bake-out | 1 MΩ or more |
| Branch circuit | R11 | Clamp meter on each heater group at full power | Under 16 A in all; about 6.25 A per group |
| Independent limit | R10 | Heat the T3 input (or a thermocouple simulator) past 600 °C with the heaters on | The contactor opens both legs and stays open until reset by hand |
| Fail-safe | R12 | Reset the controller, unplug a thermocouple, cut the export signal | Heaters off and damper closed within 60 s each time |
| Charge follows export | R2 | Log export and heater power through a sunny day | Heater power tracks surplus in 25 W steps; little or no grid import |
| Well wall and sand limit | R8 | Log T1, T2 and T4 to T7 through a full charge; a temporary thermocouple on the drum wall beside an outer well | Well walls 550 °C or less; drum wall 500 °C or less |
| Jacket and cap surfaces | R9, R13 | Contact probe at full charge: jacket side and top, and the cap at the edge of the outlet hole | Jacket 45 °C or less; cap edge under 200 °C |
| Supply air | R6 | Log the supply air sensor through a discharge | 55 °C or less at all times |
| Stored heat | R1 | Calorimetric discharge from full (air flow and temperature rise) | 18 kWh(th) or more between 150 and 450 °C |
| Heater service | R17 | Lift the cap and the top insulation, draw one heater, refit it | Done without disturbing the sand |

## 6. Safety stops

Stop at each point. Carry on only when everything listed is true.

- **S1. Before cutting firebrick or pouring sand.** Work outdoors or with local exhaust; P100 or N95 respirator, eye protection and gloves on; the area wet-cleaned afterwards, never dry-swept.
- **S2. Before handling fiber insulation.** Gloves, long sleeves, eye protection and a respirator; offcuts bagged.
- **S3. Before burning out the drum.** Outdoors, clear of buildings, with water to hand; the drum empty, open and never sealed.
- **S4. Before the top insulation covers the heaters.** Every heater reads 1 MΩ or more at 500 V lead to sheath; every lead is labelled and its beads are whole.
- **S5. Before the 240 V circuit is energized.** A licensed electrician has run and checked the dedicated circuit; the enclosure is closed and earthed; the junction box lid is on; the high limit trips the contactor in a test with the heaters disconnected.
- **S6. Before the first firing (bake-out).** The room is ventilated and smoke detectors are not disabled; the hot outlet guard is fitted and nothing combustible is within 450 mm of it; all five warning labels are on; someone stays with the unit until it holds 150 °C steadily.
- **S7. Before any heater is pulled or the lid opened.** The sand mean reads below 60 °C; the circuit is isolated and locked off.

## 7. Tools, skills and workspace

**Tools.** Pipe threader for 3/4 and 1-1/4 in (rental) with cutting oil; pipe cutter or hacksaw; two pipe wrenches; reamer; bi-metal hole saws 6 to 106 mm and a drill with a side handle; step drill; aviation snips; hand seamer (folding pliers); rivet gun for 4.8 mm rivets; sheet metal screwdriver bits; coarse handsaw or masonry blade for firebrick; long serrated insulation knife; trammel or string and nail; tape, steel rule and square; two ratchet straps; flap disc and angle grinder for paint stripping; 500 V insulation tester; multimeter with a type K input; clamp meter; kitchen or platform scale for the sand bags.

**Skills.** Pipe cutting and threading, sheet metal layout, cutting, folding and riveting, careful handling of fiber and dust. The 240 V circuit and enclosure wiring need a licensed electrician; everything else needs no certified trade.

**Workspace.** The final position on a concrete slab inside the heated space, with about 1 m of clear floor round it; an outdoor area for burning out the drum, cutting brick and pouring dusty materials; a bench with a pipe vice.

**Personal protective equipment.** P100 or N95 respirator for sand, brick and fiber; safety glasses; cut-resistant gloves for sheet metal; leather gloves for the drum burn-out; hearing protection for grinding.

## 8. Where the numbers come from

- Model and constructability checks: `cad/src/model.py` (`python cad/src/model.py --check`, 88 checks); STEP and STL in `cad/step/` and `cad/stl/`.
- Pictures: `cad/src/build_plan_media.py`, using `.kit/build_views.py`; written to `docs/05-build-plan/` and `cad/drawings/TBK-DWG-101` to `TBK-DWG-110`.
- General arrangement: `cad/drawings/TBK-DWG-001.pdf`, Rev P3.
- Calculations: `docs/04-calcs/TBK-CAL-001-sizing.md` (TBK-CAL-001 v0.5) and `docs/04-calcs/tbk_cal_001.py`; mass and floor load section 7, electrical section 6.
- Bill of materials: `bom/bom.csv` and `bom/bom-notes.md`.
- Decisions: `docs/decisions/0003-design-for-construction.md` (TBK-DDR-003), with TBK-DDR-002; open items in `docs/06-design-decisions.md` (TBK-DEC-001).
- Requirements: `docs/03-requirements.md` (TBK-REQ-001 v0.12).
