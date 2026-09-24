# ThermaBrick

**Area:** CleanTech · **Status:** Concept · **Prototype budget:** about $600 USD target (v0.2 estimate $3,674, under review) · **Difficulty:** 3 of 5

Sand thermal battery in an insulated steel drum. Resistive elements charge it from surplus PV, and a fan pulls hot air out for space heating.

## Problem

Surplus rooftop solar gets exported cheaply or curtailed, while heating still burns gas.

## Concept

Sand thermal battery in an insulated steel drum. Resistive elements charge it from surplus PV, and a fan pulls hot air out for space heating.

The v0.2 design stores 18.3 kWh(th) in 210 kg of sand between 150 °C and 450 °C. Twelve 250 W heaters charge it at up to 3.0 kW, filling it in 7.9 h, and six steel U-tubes deliver 1.0 kW of warm air for about 18 h.

| Document | ID | Version |
| --- | --- | --- |
| [Problem statement](docs/01-problem.md) | TBK-PRB-001 | 0.2 |
| [Design precis](docs/02-concept.md) | TBK-PRC-001 | 0.2 |
| [Requirements](docs/03-requirements.md) | TBK-REQ-001 | 0.2 |
| [Thermal and electrical sizing](docs/04-calcs/TBK-CAL-001-sizing.md) | TBK-CAL-001 | 0.1 |
| [General arrangement](cad/drawings/TBK-DWG-001.pdf) | TBK-DWG-001 | Rev P1 |

## Key components

- 55 gal open-head steel drum, unlined
- Sand, 210 kg
- AES fiber blanket and stone wool insulation
- Nichrome cartridge heaters, 12 x 250 W, in steel wells
- Six 1-1/4 in steel U-tubes (discharge heat exchanger)
- Solid state relays and a safety contactor
- K-type thermocouples and an independent high-limit controller
- ESP32 controller and PV export meter
- Inline fan with mixing tee

The working bill of materials is in [bom/bom.csv](bom/bom.csv).

## Safety

> Operates at up to 550 °C inside and weighs about 410 kg. Use a dedicated GFCI-protected 240 V circuit, keep the independent high limit in service, and stand the unit on a concrete slab. See TBK-PRC-001, sections 6 and 7.

## Repository layout

| Folder | Contents |
| --- | --- |
| `docs/` | Problem, concept, requirements, calculations and design decisions |
| `cad/src/` | build123d Python source, the source of truth for all geometry |
| `cad/step/`, `cad/stl/` | Exported models for FreeCAD, other CAD tools and printing |
| `cad/drawings/` | 2D sketches and dimensioned drawings |
| `bom/` | Bill of materials |
| `electronics/` | KiCad schematics and PCB layouts |
| `firmware/` | Microcontroller code |
| `media/` | Renders, perspectives and photos |
| `build-log/` | Dated prototyping notes |

## Documentation

Controlled documents follow the portfolio [documentation standard](.kit/STANDARDS.md). Each carries a document ID (TBK-PRC-001 for the precis), a version and a revision history. Branded PDFs are built with `python .kit/render.py` and attached to GitHub Releases when a document is tagged, for example `TBK-PRC-001/v1.0`.

## Licenses

- **Hardware** (CAD, drawings, BOM, electronics): [CERN-OHL-S v2](LICENSE)
- **Software** (firmware, scripts, notebooks): [MIT](LICENSE-SOFTWARE)

Part of the open hardware portfolio at [amishchadha.com](https://amishchadha.com).
