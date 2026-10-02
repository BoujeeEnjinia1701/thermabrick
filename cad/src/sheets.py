"""ThermaBrick drawing sheets.

Run from the repo root:  python cad/src/sheets.py
Builds TBK-DWG-001 (general arrangement) and TBK-DWG-002 (test article general
arrangement) as SVG, PDF and PNG in cad/drawings/. Pass a drawing number to build one only.
Geometry comes from model.py; the sheet frame and title block come from .kit/drawing.py.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".kit"))
sys.path.insert(0, str(ROOT / "cad" / "src"))

from drawing import Sheet, project_views  # noqa: E402
import model  # noqa: E402

DWG = ROOT / "cad" / "drawings"
VIEWS = DWG / "_views"

REVISIONS = {
    "TBK-DWG-001": [("P1", "First issue: general arrangement of the v0.2 design", "2026-09-24", "AC"),
                    ("P2", "Made constructable: base, fittings, plenum, cap, box (TBK-DDR-003)", "2026-09-30", "AC")],
    "TBK-DWG-002": [("P1", "First issue: reduced-scale test article", "2026-09-24", "AC"),
                    ("P2", "Bricks moved under the chime; U-tube legs to 36 in nipple length; stack follows", "2026-09-24", "AC")],
    "TBK-DWG-005": [("P1", "First issue: controller enclosure, 250 x 200 x 150 mm", "2026-09-24", "AC")],
}


def project_visible(part, path, origin, up, target):
    """Visible-edge projection in the kit's line style, for section and cutaway views."""
    from build123d import ExportSVG, Unit
    visible, _ = part.project_to_viewport(origin, up, target)
    ex = ExportSVG(unit=Unit.MM, line_weight=0.35)
    ex.add_layer("Visible", line_color=0x111827)
    ex.add_shape(visible, layer="Visible")
    ex.write(str(path))
    return path


def rows_001():
    P, d = model.PARAMS, model.derived()
    return [
        ("Storage", f"{P['sand_mass_kg']:.0f} kg dry silica sand, 18.3 kWh(th) between 150 and 450 °C mean"),
        ("Charge", f"12 cartridge heaters, 250 W each, 3.0 kW at 240 V; sand and well wall 550 °C max"),
        ("Discharge", "Six 1-1/4 in U-tubes, 1.0 kW rated, 1.5 kW boost; supply air 50 °C via mixing tee"),
        ("Envelope", f"{d['overall_d']:,.0f} mm dia x {d['overall_h']:,.0f} mm high; about 415 kg; slab floor only"),
        ("Section A-A", "Front view is cut on the XZ plane through four heater wells; sand omitted for clarity"),
        ("Sand level", f"{d['sand_depth']:.0f} mm above drum floor; headspace filled with {d['ins_top_int']:.0f} mm "
                       "AES blanket and stone wool"),
        ("Reference", "TBK-PRC-001 design precis, TBK-CAL-001 sizing, TBK-BLD-001 build plan, bom/bom.csv"),
    ]


def rows_002():
    P, d = test_article.PARAMS, test_article.derived()
    return [
        ("Storage", f"{P['sand_mass_kg']:.0f} kg dry silica sand, 5.9 kWh(th) between 150 and 450 °C mean"),
        ("Charge", "4 cartridge heaters, 250 W each, 1.0 kW at 120 V plug-in; well wall 550 °C max"),
        ("Discharge", "One 1-1/4 in U-tube, 12 V blower on the inlet leg, 4 in dilution stack on the outlet"),
        ("Envelope", f"{d['overall_d']:,.0f} mm dia x {d['overall_h']:,.0f} mm high incl. stack; about 115 kg"),
        ("Section A-A", "Front view is cut on the XZ plane; sand omitted for clarity"),
        ("Sand level", f"{d['sand_depth']:.0f} mm above drum floor; wells and cells match the full-scale design"),
        ("Reference", "TBK-PRC-002 test article precis, TBK-CAL-002 sizing, bom/bom-test-article.csv"),
    ]


def rows_005():
    P, d = enclosure.PARAMS, enclosure.derived()
    return [
        ("Enclosure", f"{P['width']:.0f} x {P['height']:.0f} x {P['depth']:.0f} mm polycarbonate, UL 94 V-0 or 5VA, IP65; "
                      "steel mounting plate bonded to PE"),
        ("Lid cutouts", f"REX-C100 {P['rex_cutout']:.0f} x {P['rex_cutout']:.0f} mm at x {P['rex_xz'][0]:.0f}, z {P['rex_xz'][1]:.0f}; "
                        f"STOP and START {P['button_hole']:.1f} mm dia at x {P['stop_xz'][0]:.0f} and {P['start_xz'][0]:.0f}, z 55"),
        ("Glands", "Bottom face at y 75: M25 x -80 (thermocouples), M16 x -35 (blower), M20 x 55 (supply), M20 x 95 (heaters)"),
        ("Plate", "DIN rail at z 145: HDR-15-12 12 V supply, JQX-30F relay socket. SSR on heat sink top right; controller bottom left"),
        ("Clearance", f"Fit check: every part clears by {P['clearance']:.0f} mm; REX-C100 body ends 36 mm from the plate"),
        ("Datum", "x from the enclosure centerline, z up from the bottom face, y into the box from the lid"),
        ("Reference", "TBK-DWG-003 schematic, TBK-PRC-002, bom/bom-test-article.csv"),
    ]


def key_data_svg(path, rows):
    """Key data and notes panel, placed under the orthographic views."""
    w, rh = 205.0, 5.4
    h = rh * (len(rows) + 1) + 1
    ink, muted, rule, accent = "#111827", "#4B5563", "#9CA3AF", "#0F766E"
    font = "IBM Plex Sans, Helvetica, Arial, sans-serif"
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">',
           f'<rect x="0" y="0" width="{w}" height="{h}" fill="#FFFFFF" stroke="{ink}" stroke-width="0.35"/>',
           f'<rect x="0" y="0" width="2" height="{h}" fill="{accent}"/>',
           f'<text x="5" y="4" font-family="{font}" font-size="2.2" font-weight="600" fill="{ink}">KEY DATA AND NOTES</text>']
    for i, (k, v) in enumerate(rows, start=1):
        y = i * rh
        out.append(f'<line x1="2" y1="{y:.1f}" x2="{w}" y2="{y:.1f}" stroke="{rule}" stroke-width="0.2"/>')
        out.append(f'<text x="5" y="{y + 3.7:.1f}" font-family="{font}" font-size="2.1" font-weight="500" '
                   f'fill="{muted}">{k.upper()}</text>')
        out.append(f'<text x="34" y="{y + 3.7:.1f}" font-family="{font}" font-size="2.3" fill="{ink}">{v}</text>')
    out.append("</svg>")
    path.write_text("".join(out))
    return path


SHEETS = {
    "TBK-DWG-001": dict(mod=model, title="General arrangement", rows=rows_001,
                        material="Carbon steel drum and pipe; AES blanket and stone wool; galvanized jacket. "
                                 "See bom/bom.csv"),
    # TBK-DWG-002 to TBK-DWG-005 (test article, controller) were moved to
    # archive/out-of-phase-trl4/ on 2026-09-25; that copy of sheets.py still builds them.
}


def _solid(shapes):
    """Drop empty results of a boolean (a part lying wholly on the removed side)."""
    return [s for s in shapes if getattr(s, "_wrapped", None) is not None and s.volume > 0]


def make(dwg_no):
    from build123d import Box, Pos, Compound, Align

    cfg = SHEETS[dwg_no]
    assy, parts = cfg["mod"].build(parts=True)
    vdir = VIEWS / dwg_no
    views = project_views(assy, vdir)                       # front, top, right, iso of the full unit
    bb = assy.bounding_box()
    c = bb.center()
    dist = max(bb.size.X, bb.size.Y, bb.size.Z) * 10
    big = 4000

    def visible(part, name, origin):
        return project_visible(part, vdir / f"{name}.svg", origin, (0, 0, 1), (c.X, c.Y, c.Z))

    # Section A-A: keep y >= 0, drop the sand, view from -Y
    keep = Pos(0, big / 2, 0) * Box(big, big, big, align=(Align.CENTER, Align.CENTER, Align.MIN))
    names = getattr(cfg["mod"], "ASSEMBLY", list(parts))
    sec = Compound(_solid([parts[n] & keep for n in names if n != "sand"]))
    views["front"] = visible(sec, "section_aa", (c.X, c.Y - dist, c.Z))
    # Right view: exterior, visible edges only
    views["right"] = visible(assy, "right_exterior", (c.X + dist, c.Y, c.Z))
    # Isometric cutaway: remove the quadrant facing the viewer (x > 0, y < 0), sand kept.
    # A sheet may instead drop named parts (the enclosure lid) and skip the cut.
    quad = Pos(big / 2, -big / 2, -10) * Box(big, big, big, align=(Align.CENTER, Align.CENTER, Align.MIN))
    keep_parts = [n for n in names if n not in cfg.get("iso_drop", ())]
    if cfg.get("iso_cut", True):
        cut = Compound(_solid([parts[n] - quad for n in keep_parts]))
    else:
        cut = Compound([parts[n] for n in keep_parts])
    ix, iy, iz = cfg.get("iso_dir", (1.0, -1.0, 0.8))
    views["iso"] = visible(cut, "iso_cutaway", (c.X + dist * ix, c.Y + dist * iy, c.Z + dist * iz))

    revs = REVISIONS[dwg_no]
    s = Sheet(project="ThermaBrick", title=cfg["title"], dwg_no=dwg_no, rev=revs[-1][0], author="Amish Chadha",
              date=revs[-1][2], scale=None, material=cfg["material"], revisions=revs)
    s.add_ortho(views, ["front", "top", "right"])
    iso_label, iso_sub = cfg.get("iso_label", ("Isometric cutaway", "Quarter removed, not to scale"))
    s.add_iso(views["iso"], label=iso_label, sublabel=iso_sub)
    panel = key_data_svg(vdir / "key_data.svg", cfg["rows"]())
    s.add_svg(panel, 20.0, 222.0, scale=1.0)
    out = s.save(DWG / dwg_no)
    print(f"wrote {out.relative_to(ROOT)} and PDF/PNG (scale 1:{1 / s.scale:g})")


if __name__ == "__main__":
    for dwg in (sys.argv[1:] or list(SHEETS)):
        make(dwg)
