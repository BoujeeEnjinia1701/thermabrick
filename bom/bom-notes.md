# BOM notes

The v0.2 bill of materials in `bom.csv` totals **$3,673.50** (Table 1). The prototype target in TBK-PRB-001 is about $600, so the full-scale design costs about six times the target. The budget decision is open (TBK-PRB-001, section 5).

| Group | Cost (USD) | Share |
| --- | --- | --- |
| Insulation | 839.00 | 23 % |
| Controls and instrumentation | 818.50 | 22 % |
| Heaters and wells | 728.00 | 20 % |
| Discharge exchanger and air path | 728.00 | 20 % |
| Storage vessel and sand | 215.00 | 6 % |
| Branch circuit | 190.00 | 5 % |
| Jacket | 155.00 | 4 % |
| Total | 3,673.50 | 100 % |

*Table 1. BOM cost by group.*

## Cost basis

- Unit costs are budgetary estimates in US dollars, based on typical US retail and distributor list prices in September 2026, before tax and shipping. They are not quotes. Confirm every price at order.
- Suppliers are examples of where each part can be bought. "Or equal" means any part that meets the spec column.
- Quantities include cutting allowance: 227 kg of sand is bought for a 210 kg fill, and pipe comes in full 10 ft sticks.
- Excluded: tool purchase or rental (pipe threader, hole saws), electrician labor for the branch circuit, permits, and the room thermostat if one is added.
- Quantities and dimensions follow `cad/src/model.py`. When the model changes, update this BOM in the same commit (CONTRIBUTING.md).

## Cost-down options

These options would bring the total to roughly $2,400 to $2,700 with no change in performance. None of them reaches $600 at 18 kWh(th), so the budget decision stands.

| Option | Saving | Trade-off |
| --- | --- | --- |
| Generic import cartridge heaters instead of US industrial brands | About $300 | Wider tolerance on resistance and weaker lead insulation; test each on arrival |
| Reconditioned open-head drum | About $100 | Must be unlined and free of residues; burn out before use |
| Read export from the inverter's local API instead of an energy meter | $90 | Works only with supported inverters |
| MAX31855 amplifiers instead of MAX31856 | About $50 | Type K only, which is all this design uses |
| Stone wool batts for the base instead of board, loads carried by firebrick under the full base | About $100 | More firebrick; slightly higher base loss |
| Existing 240 V circuit or breaker | Up to $190 | Site dependent |

*Table 2. Cost-down options.*

A reduced-scale test article is the only route to $600. For example, a 30 US gal drum with about 70 kg of sand, four heaters and two U-tubes would store about 6 kWh(th). It would test the charge model, the controls and the ratcheting behavior before the full-scale build.
