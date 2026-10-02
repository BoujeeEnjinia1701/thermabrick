#!/usr/bin/env python3
"""Concept media for ThermaBrick (kit 1.3.0, CLAUDE.md section 5).

Run from the repo root:
    python cad/src/concept_media.py

Builds the full-scale assembly from model.py and writes, through .kit/concept.py (kit 1.3.0):
    media/hero.png                 shaded isometric render with a 1.75 m person for scale
    media/model.glb, viewer.html   interactive 3D viewer for the website
    media/flow.png                 estimated heat flow, full to empty
    media/cutaway.png              half section showing the sand, wells, heaters and U-tubes
    media/exploded.png             exploded view with callouts numbered by bom/bom.csv line
    media/concept-blueprint.*      concept sheet TBK-DWG-006 Rev P3 (P1 had no scale figure; P3 follows TBK-DDR-003)
Key figures come from TBK-CAL-001 v0.2. Licensed MIT (see LICENSE-SOFTWARE).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".kit"))
sys.path.insert(0, str(ROOT / "cad" / "src"))

from concept import Part, render_all  # noqa: E402
import model  # noqa: E402

# (model part, name, color, bom/bom.csv line, exploded offset in mm)
PARTS = [
    ("base", "Insulating firebrick base", "#C9B79C", 21, (0, 0, -350)),
    ("drum", "55 gal steel drum", "#6B7280", 1, (0, 0, 0)),
    ("sand", "Sand, 210 kg fill", "#D8B26E", 2, (0, 1400, 0)),
    ("wells", "Heater well pipe", "#374151", 4, (0, 0, 900)),
    ("heaters", "Cartridge heaters", "#B91C1C", 3, (0, 0, 1500)),
    ("utubes", "U-tube pipe", "#1F2937", 6, (0, 0, 0)),
    ("lid", "Drum lid (with drum)", "#4B5563", None, (0, 0, 650)),
    ("collector", "Collector shell", "#111827", 10, (0, 0, 2100)),
    ("insulation", "Stone wool batt", "#E5D3A8", 22, (-1500, 0, 0)),
    ("jacket", "Jacket sheet", "#9CA3AF", 25, (1500, 0, 0)),
    ("jacket_cap", "Jacket cap (jacket sheet)", "#9CA3AF", None, (0, 0, 1600)),
    ("trim_ring", "Outlet trim ring", "#1F2937", 44, (0, 0, 1700)),
    ("inlet_plenum", "Inlet plenum (jacket sheet)", "#6B7280", None, (0, 0, 1800)),
    ("jbox", "Heater junction box", "#4B5563", 42, (0, 0, 1900)),
]

KEY_FIGURES = [
    "18.3 kWh(th) stored, 150 to 450 °C",
    "210 kg silica sand in a 55 US gal drum",
    "3.0 kW charge, 12 x 250 W heaters, 240 V",
    "Full charge 9.6 h (R3 asks 8 h: not met)",
    "1.0 kW warm air held for 14.3 h",
    "Standby loss 459 W at full charge",
    "1,209 mm dia. x 1,462 mm high",
    "Source: TBK-CAL-001 v0.3",
]

# Discharge from full to empty, TBK-CAL-001 v0.2, section 4 (calculated estimates, not measured)
FLOW = {
    "title": "estimated heat flow, full to empty (TBK-CAL-001)",
    "stages": [("Sand store, full", 18.3), ("Warm air output", 14.5)],
    "losses": [(0, "Standby loss into the room", 3.8)],
    "unit": "kWh",
}


def main():
    _, out = model.build(parts=True)
    parts = [Part(name, out[key], color, bom, explode) for key, name, color, bom, explode in PARTS]
    res = render_all(parts, project="ThermaBrick", title="Concept overview", dwg_no="TBK-DWG-006",
                     key_figures=KEY_FIGURES, date="2026-09-30", media_dir=str(ROOT / "media"), flow=FLOW,
                     rev="P3")
    for k, v in res.items():
        print(f"{k:10s} {Path(v).relative_to(ROOT)}")


if __name__ == "__main__":
    main()
