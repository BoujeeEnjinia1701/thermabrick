# BOM notes

The bill of materials in `bom.csv` totals **$3,868.50** for the constructable design (Table 1). It was $3,673.50 for the v0.2 concept; making the design buildable (TBK-DDR-003, 2026-09-30) added $180.00: longer heater leads and thermocouple sheaths, 4 in nipples, two more firebricks, a second AES rope, more fasteners, and four new lines (setting template, outlet trim ring, thermocouple guide rods and cap grommets, lines 43 to 46). The warning labels approved on 2026-10-02 (line 47, $15.00) bring the total to $3,868.50.

Value-engineering target: USD 728 (`budget_usd` in `project.yaml`, set as the reduced-scale test article budget, decided by Amish on 2026-09-25, TBK-DDR-002; the concept's original target was about $600). Estimated cost of the constructable design: USD 3,869 (USD 3,141 over the target). The target is a hypothetical control figure for value engineering, not a spending limit.

| Group | Cost (USD) | Share |
| --- | --- | --- |
| Insulation | 871.00 | 23 % |
| Controls and instrumentation | 862.50 | 22 % |
| Heaters and wells | 776.00 | 20 % |
| Discharge exchanger and air path | 740.00 | 19 % |
| Storage vessel, sand and setting template | 233.00 | 6 % |
| Branch circuit | 190.00 | 5 % |
| Jacket, trim ring, grommets and warning labels | 196.00 | 5 % |
| Total | 3,868.50 | 100 % |

*Table 1. BOM cost by group.*

## Cost basis

- Unit costs are budgetary estimates in US dollars, based on typical US retail and distributor list prices in September 2026, before tax and shipping. They are not quotes. Confirm every price at order.
- Suppliers are examples of where each part can be bought. "Or equal" means any part that meets the spec column.
- Quantities include cutting allowance: 227 kg of sand is bought for a 210 kg fill, and pipe comes in full 10 ft sticks.
- Excluded: tool purchase or rental (pipe threader, hole saws), electrician labor for the branch circuit, permits, and the room thermostat if one is added.
- Quantities and dimensions follow `cad/src/model.py`. When the model changes, update this BOM in the same commit (CONTRIBUTING.md).

## Cost-down options

These options together save about $830 (to about $3,040) with no change in performance. None of them reaches the value-engineering target at 18 kWh(th).

| Option | Saving | Trade-off |
| --- | --- | --- |
| Generic import cartridge heaters instead of US industrial brands | About $300 | Wider tolerance on resistance and weaker lead insulation; test each on arrival |
| Reconditioned open-head drum | About $100 | Must be unlined and free of residues; burn out before use |
| Read export from the inverter's local API instead of an energy meter | $90 | Works only with supported inverters |
| MAX31855 amplifiers instead of MAX31856 | About $50 | Type K only, which is all this design uses |
| Stone wool batts for the base instead of board, loads carried by firebrick under the full base | About $100 | More firebrick; slightly higher base loss |
| Existing 240 V circuit or breaker | Up to $190 | Site dependent |

*Table 2. Cost-down options.*

A reduced-scale test article is the only route to a cost near the target. It was the next build, and is now archived and on hold with TRL 4. It is a 16 US gal drum with 68 kg of sand, four heater cells and one U-tube, storing 5.9 kWh(th) (TBK-PRC-002). Its separate BOM, `archive/out-of-phase-trl4/bom/bom-test-article.csv`, is estimated at $727.70. Modeling the controller enclosure (TBK-DWG-005) added $36.00. The resulting $635.70 was accepted as the test article budget on 2026-09-24. The build procedure then added a second stone wool pack, the heater cable, wiring consumables and thermocouple extension wire ($92.00), for $727.70. Decided by Amish, 2026-09-25: go with recommendation, so the test article budget is $727.70 (TBK-DDR-002). Nothing will be bought while TRL 4 is on hold. The optional controller board (`archive/out-of-phase-trl4/bom/bom-controller-board.csv`, TBK-DWG-004), kept deferred by Amish's 2026-09-25 decision, would add $24.85 net, taking the test article to $752.55, so it is not part of the $600 baseline. An earlier note here suggested a 30 US gal drum. Sizing showed that drum gives a bed too shallow for the full-scale heaters, so the 16 US gal drum replaced it.

The purchasing checklist and its generator, `checklist.py`, are archived with the test article under `archive/out-of-phase-trl4/bom/`.

Decisions of 2026-10-02 (TBK-DEC-001), carried into the bill of materials the same day:

- Line 39 is now a 2-pole 20 A, 5 mA GFCI breaker; the price stays at $110.00 (basis: a Class A 2-pole GFCI breaker for a typical residential panel is within the same price band as the 30 mA type it replaces; confirm at order). 30 mA equipment ground-fault protection only as a measured exception agreed with the installing electrician.
- Line 47 (new, $15.00): five self-adhesive vinyl warning labels rated 105 C or higher, at about $3 each: HOT SURFACES INSIDE (jacket), HOT OUTLET (jacket cap), HOT SURFACE (outlet guard sleeve), DANGER 240 V (junction box) and DANGER 240 V (control enclosure). Positions are in TBK-BLD-001 step 22. The labels add about 0.05 kg; operating mass stays 415 kg.
- The teal top bead and kick plinth in the renders are optional cosmetic parts with no BOM line; the black outlet trim ring (line 44) is a functional part and is drawn as such in the appearance model.
