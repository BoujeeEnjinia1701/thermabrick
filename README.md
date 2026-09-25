# ThermaBrick

**Area:** CleanTech · **TRL:** 3 of 9 (proof of concept) · **Status:** Concept · **Prototype budget:** $635.70 USD test article (decided by Amish; on hold with TRL 4) (full-scale estimate $3,674) · **Difficulty:** 3 of 5

Sand thermal battery in an insulated steel drum. Resistive elements charge it from surplus PV, and a fan pulls hot air out for space heating.


> **Out-of-phase work archived (2026-09-25).** The portfolio is capped at TRL 3, and TRL 4 is on hold by Amish's instruction. The reduced-scale test article, its test plan and report template, firmware, controller schematic and board, enclosure, purchasing checklist, build procedure and cut list were made in an earlier session that went past the cap. They are kept, unchanged and with full history, in [archive/out-of-phase-trl4/](archive/out-of-phase-trl4/README.md), and are not current work.

## Problem

Surplus rooftop solar gets exported cheaply or curtailed, while heating still burns gas.

## Concept

Sand thermal battery in an insulated steel drum. Resistive elements charge it from surplus PV, and a fan pulls hot air out for space heating.

The v0.2 design stores 18.3 kWh(th) in 210 kg of sand between 150 °C and 450 °C. Twelve 250 W heaters charge it at up to 3.0 kW, filling it in 9.6 h, and six steel U-tubes deliver 1.0 kW of warm air for about 14 h. A reduced-scale test article (about 6 kWh(th), $600) comes first, to measure the sand and insulation properties the design depends on.

| Document | ID | Version |
| --- | --- | --- |
| [Problem statement](docs/01-problem.md) | TBK-PRB-001 | 0.7 |
| [Design precis](docs/02-concept.md) | TBK-PRC-001 | 0.4 |
| [Requirements](docs/03-requirements.md) | TBK-REQ-001 | 0.8 |
| [Thermal and electrical sizing](docs/04-calcs/TBK-CAL-001-sizing.md) | TBK-CAL-001 | 0.2 |
| [General arrangement](cad/drawings/TBK-DWG-001.pdf) | TBK-DWG-001 | Rev P1 |
| [Concept sheet](media/concept-blueprint.pdf), with [hero](media/hero.png), [cutaway](media/cutaway.png) and [exploded](media/exploded.png) renders, [heat flow](media/flow.png) and [3D viewer](media/viewer.html) | TBK-DWG-006 | Rev P2 |
| [Purchasing checklist](bom/purchasing-checklist.md) | | Test article, by supplier |
| [Controller board BOM (optional, deferred)](bom/bom-controller-board.csv) | | +$24.85 net |

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
