"""ThermaBrick drawing sheets.

Run from the repo root:  python cad/src/sheets.py
Builds TBK-DWG-001 (general arrangement) as SVG, PDF and PNG in cad/drawings/.
Geometry comes from model.py; the sheet frame and title block come from .kit/drawing.py.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".kit"))
sys.path.insert(0, str(ROOT / "cad" / "src"))

from drawing import Sheet, project_views  # noqa: E402
from model import PARAMS as P, build, derived  # noqa: E402

DWG = ROOT / "cad" / "drawings"
VIEWS = DWG / "_views"

REVISIONS = [
    ("P1", "First issue: general arrangement of the v0.2 design", "2026-09-24", "AC"),
]


def project_visible(part, name, origin, up, target):
    """Visible-edge projection in the kit's line style, for section and cutaway views."""
    from build123d import ExportSVG, Unit
    visible, _ = part.project_to_viewport(origin, up, target)
    ex = ExportSVG(unit=Unit.MM, line_weight=0.35)
    ex.add_layer("Visible", line_color=0x111827)
    ex.add_shape(visible, layer="Visible")
    path = VIEWS / f"{name}.svg"
    ex.write(str(path))
    return path


def key_data_svg(path):
    """Key data and notes panel, placed under the orthographic views."""
    d = derived()
    rows = [
        ("Storage", f"{P['sand_mass_kg']:.0f} kg dry silica sand, 18.3 kWh(th) between 150 and 450 °C mean"),
        ("Charge", f"12 cartridge heaters, 250 W each, 3.0 kW at 240 V; sand and well wall 550 °C max"),
        ("Discharge", "Six 1-1/4 in U-tubes, 1.0 kW rated, 1.5 kW boost; supply air 50 °C via mixing tee"),
        ("Envelope", f"{d['overall_d']:,.0f} mm dia x {d['overall_h']:,.0f} mm high; about 410 kg; slab floor only"),
        ("Section A-A", "Front view is cut on the XZ plane through four heater wells; sand omitted for clarity"),
        ("Sand level", f"{d['sand_depth']:.0f} mm above drum floor; headspace filled with {d['ins_top_int']:.0f} mm "
                       "AES blanket and stone wool"),
        ("Reference", "TBK-PRC-001 design precis, TBK-CAL-001 sizing, bom/bom.csv"),
    ]
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


def main():
    from build123d import Box, Pos, Compound, Align

    assy, parts = build(parts=True)
    d = derived()
    views = project_views(assy, VIEWS)                      # front, top, right, iso of the full unit
    bb = assy.bounding_box()
    c = bb.center()
    dist = max(bb.size.X, bb.size.Y, bb.size.Z) * 10
    big = 4000

    # Section A-A: keep y >= 0, drop the sand, view from -Y
    keep = Pos(0, big / 2, 0) * Box(big, big, big, align=(Align.CENTER, Align.CENTER, Align.MIN))
    sec = Compound([parts[n] & keep for n in parts if n != "sand"])
    views["front"] = project_visible(sec, "section_aa", (c.X, c.Y - dist, c.Z), (0, 0, 1), (c.X, c.Y, c.Z))

    # Right view: exterior, visible edges only
    views["right"] = project_visible(assy, "right_exterior", (c.X + dist, c.Y, c.Z), (0, 0, 1), (c.X, c.Y, c.Z))

    # Isometric cutaway: remove the quadrant facing the viewer (x > 0, y < 0), sand kept
    quad = Pos(big / 2, -big / 2, -10) * Box(big, big, big, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cut = Compound([parts[n] - quad for n in parts])
    views["iso"] = project_visible(cut, "iso_cutaway", (c.X + dist, c.Y - dist, c.Z + dist * 0.8), (0, 0, 1),
                                   (c.X, c.Y, c.Z))

    s = Sheet(project="ThermaBrick", title="General arrangement", dwg_no="TBK-DWG-001",
              rev=REVISIONS[-1][0], author="Amish Chadha", date=REVISIONS[-1][2], scale=None,
              material="Carbon steel drum and pipe; AES blanket and stone wool; galvanized jacket. See bom/bom.csv",
              revisions=REVISIONS)
    s.add_ortho(views, ["front", "top", "right"])
    s.add_iso(views["iso"], label="Isometric cutaway", sublabel="Quarter removed, not to scale")
    panel = key_data_svg(VIEWS / "key_data.svg")
    s.add_svg(panel, 20.0, 222.0, scale=1.0)
    out = s.save(DWG / "TBK-DWG-001")
    print(f"wrote {out.relative_to(ROOT)} and PDF/PNG (scale 1:{1 / s.scale:g})")


if __name__ == "__main__":
    main()
