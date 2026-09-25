"""ThermaBrick test article controller enclosure (build123d), TBK-DWG-005.

Run from the repo root:  python cad/src/enclosure.py
Checks the fit of every part, then exports STEP and STL to cad/step and cad/stl as
thermabrick-controller-enclosure.*. The sheet is built by cad/src/sheets.py.

The enclosure holds the controller of TBK-DWG-003: mains parts, the 12 V supply and the
low-voltage controller (hand-wired modules or the optional board, TBK-DWG-004, which have
the same envelope). Parts are modeled as their outline envelopes from supplier data.

Frame: origin at the bottom front center of the enclosure. +X right, +Y into the box
(lid at y = 0, back wall at y = depth), +Z up. Millimeters.
"""
from pathlib import Path

PARAMS = {
    # Enclosure: polycarbonate wall box, UL 94 V-0 or 5VA, IP65, with a steel mounting plate
    "width": 250.0, "height": 200.0, "depth": 150.0, "wall": 3.0,
    "plate_standoff": 8.0, "plate_t": 2.0, "plate_margin": 10.0,
    # DIN rail TS35 x 7.5
    "rail_z": 145.0, "rail_x": (-112.0, 40.0),
    # Supplier envelopes: (x size, z size, y size from the plate or lid)
    "psu": (17.5, 90.0, 54.5),          # Mean Well HDR-15-12 on the rail
    "relay": (40.0, 60.0, 80.0),        # JQX-30F 2Z on its DIN socket
    "ssr": (60.0, 80.0, 80.0),          # SSR-25DA on its heat sink, fins vertical
    "controller": (110.0, 80.0, 55.0),  # controller board or modules on standoffs
    "wago": (20.0, 18.0, 8.0),          # lever connector, 5-way
    "rex_bezel": (48.0, 48.0, 10.0), "rex_body": (45.0, 45.0, 98.0), "rex_cutout": 45.0,
    "button_d": 30.0, "button_hole": 22.5, "button_depth": 45.0, "button_front": 12.0,
    # Positions (x, z) of part centers
    "psu_x": -91.0, "relay_x": -50.0,
    "ssr_xz": (80.0, 150.0), "controller_xz": (-55.0, 52.0),
    "wago_xz": ((45.0, 40.0), (70.0, 40.0)),
    "rex_xz": (60.0, 55.0), "stop_xz": (-25.0, 55.0), "start_xz": (10.0, 55.0),
    # Cable glands in the bottom face: (label, thread, x); dome height below, nut height above
    "glands": (("TC bundle", 25.0, -80.0), ("blower", 16.0, -35.0), ("supply", 20.0, 55.0),
               ("heater out", 20.0, 95.0)),
    "gland_dome": 22.0, "gland_nut": 6.0,
    "pe_stud_xz": (105.0, 22.0),
    "clearance": 3.0,                   # wiring clearance between part envelopes
}


def derived(p=PARAMS):
    d = {}
    w = p["wall"]
    d["inner"] = (p["width"] - 2 * w, p["height"] - 2 * w, p["depth"] - 2 * w)
    d["plate_front_y"] = p["depth"] - w - p["plate_standoff"] - p["plate_t"]   # parts stand on this face
    d["lid_inner_y"] = w
    d["usable_depth"] = d["plate_front_y"] - d["lid_inner_y"]
    return d


def build(parts=False):
    from build123d import Box, Cylinder, Pos, Rot, Compound, Align

    p, d = PARAMS, derived()
    W, H, D, t = p["width"], p["height"], p["depth"], p["wall"]
    yp = d["plate_front_y"]
    MIN = (Align.CENTER, Align.MIN, Align.CENTER)

    def box_at(x, z, sx, sz, sy, y0):
        """Box of size sx (X), sy (Y), sz (Z) centered on (x, z), spanning y0 to y0 + sy."""
        return Pos(x, y0, z) * Box(sx, sy, sz, align=MIN)

    def on_plate(x, z, size):
        sx, sz, sy = size
        return box_at(x, z, sx, sz, sy, yp - sy)

    out = {}
    # Enclosure body (open front) and lid, with cutouts
    shell = Pos(0, 0, 0) * Box(W, D, H, align=(Align.CENTER, Align.MIN, Align.MIN))
    shell -= Pos(0, -1, t) * Box(W - 2 * t, D - t + 1, H - 2 * t, align=(Align.CENTER, Align.MIN, Align.MIN))   # open at the lid
    lid = Box(W, t, H, align=(Align.CENTER, Align.MIN, Align.MIN))
    rx, rz = p["rex_xz"]
    lid -= Pos(rx, 0, rz) * Box(p["rex_cutout"], 3 * t, p["rex_cutout"], align=(Align.CENTER, Align.CENTER, Align.CENTER))
    for key in ("stop_xz", "start_xz"):
        bx, bz = p[key]
        lid -= Pos(bx, 0, bz) * Rot(90, 0, 0) * Cylinder(p["button_hole"] / 2, 3 * t)
    for _label, thread, gx in p["glands"]:
        shell -= Pos(gx, D / 2, 0) * Cylinder((thread + 0.5) / 2, 3 * t)
    out["enclosure"] = shell
    out["lid"] = lid

    # Mounting plate and DIN rail
    pm = p["plate_margin"]
    out["plate"] = box_at(0, H / 2, W - 2 * t - 2 * pm, H - 2 * t - 2 * pm, p["plate_t"], yp)
    x1, x2 = p["rail_x"]
    out["rail"] = box_at((x1 + x2) / 2, p["rail_z"], x2 - x1, 35.0, 7.5, yp - 7.5)

    # Plate-mounted parts
    out["psu"] = on_plate(p["psu_x"], p["rail_z"], p["psu"])
    out["relay"] = on_plate(p["relay_x"], p["rail_z"], p["relay"])
    out["ssr"] = on_plate(*p["ssr_xz"], p["ssr"])
    out["controller"] = on_plate(*p["controller_xz"], p["controller"])
    out["wago"] = Compound([on_plate(x, z, p["wago"]) for x, z in p["wago_xz"]])
    sx, sz = p["pe_stud_xz"]
    out["pe_stud"] = Pos(sx, yp, sz) * Rot(90, 0, 0) * Cylinder(3.0, 15.0, align=(Align.CENTER, Align.CENTER, Align.MIN))

    # Lid-mounted parts: bezels in front of the lid, bodies behind it
    bw, bh, bd = p["rex_bezel"]
    out["rex"] = box_at(rx, rz, bw, bh, bd, -bd) + box_at(rx, rz, *p["rex_body"][:2], p["rex_body"][2], t)
    buttons = []
    for key in ("stop_xz", "start_xz"):
        bx, bz = p[key]
        front = Pos(bx, 0, bz) * Rot(90, 0, 0) * Cylinder(p["button_d"] / 2, p["button_front"],
                                                           align=(Align.CENTER, Align.CENTER, Align.MIN))
        body = Pos(bx, t, bz) * Rot(-90, 0, 0) * Cylinder(12.5, p["button_depth"],
                                                          align=(Align.CENTER, Align.CENTER, Align.MIN))
        buttons.append(front + body)
    out["buttons"] = Compound(buttons)

    # Cable glands: dome below the bottom face, locknut inside
    glands = []
    for _label, thread, gx in p["glands"]:
        dome = Pos(gx, D / 2, 0) * Rot(180, 0, 0) * Cylinder(thread * 0.75, p["gland_dome"],
                                                             align=(Align.CENTER, Align.CENTER, Align.MIN))
        nut = Pos(gx, D / 2, t) * Cylinder(thread * 0.75, p["gland_nut"], align=(Align.CENTER, Align.CENTER, Align.MIN))
        glands.append(dome + nut)
    out["glands"] = Compound(glands)

    names = ["enclosure", "lid", "plate", "rail", "psu", "relay", "ssr", "controller", "wago", "pe_stud",
             "rex", "buttons", "glands"]
    assy = Compound([out[n] for n in names])
    return (assy, out) if parts else assy


def fit_check():
    """Every pair of parts must clear by the wiring clearance, and every part must sit inside
    the enclosure. Returns a list of problems (empty when everything fits)."""
    from build123d import Box, Pos, Align
    p, d = PARAMS, derived()
    _, parts = build(parts=True)
    c = p["clearance"]
    movable = ["psu", "relay", "ssr", "controller", "wago", "pe_stud", "rex", "buttons", "glands"]
    problems = []

    def grown(shape):
        bb = shape.bounding_box()
        return Pos(bb.center().X, bb.center().Y, bb.center().Z) * Box(bb.size.X + c, bb.size.Y + c, bb.size.Z + c)

    def solids(name):
        s = parts[name]
        return list(s.solids()) if hasattr(s, "solids") else [s]

    for i, a in enumerate(movable):
        for b in movable[i + 1:]:
            for sa in solids(a):
                for sb in solids(b):
                    inter = grown(sa) & grown(sb)
                    if inter.volume > 1e-3:
                        problems.append(f"{a} and {b} closer than {c} mm")
    # parts against the enclosure interior (glands, rex and buttons pass through walls by design)
    W, H, D, t = p["width"], p["height"], p["depth"], p["wall"]
    inner = Pos(0, t, t) * Box(W - 2 * t, D - 2 * t, H - 2 * t, align=(Align.CENTER, Align.MIN, Align.MIN))
    for n in ["psu", "relay", "ssr", "controller", "wago", "pe_stud"]:
        s = parts[n]
        if abs((s & inner).volume - s.volume) > 1e-3:
            problems.append(f"{n} extends outside the enclosure interior")
        if (s & parts["plate"]).volume > 1e-3:
            problems.append(f"{n} intersects the mounting plate")
    # lid-mounted bodies against plate-mounted parts
    for n in ["rex", "buttons"]:
        for m in ["psu", "relay", "ssr", "controller", "wago", "pe_stud", "rail"]:
            if (parts[n] & parts[m]).volume > 1e-3:
                problems.append(f"{n} hits {m} when the lid closes")
    return problems


def report():
    p, d = PARAMS, derived()
    yp = d["plate_front_y"]
    lines = [f"usable depth plate to lid: {d['usable_depth']:.1f} mm"]
    rex_back = p["wall"] + p["rex_body"][2]
    lines.append(f"REX-C100 body ends {yp - rex_back:.1f} mm in front of the plate; "
                 f"wiring under it is {p['wago'][2]:.0f} mm tall")
    for n in ("psu", "relay", "ssr", "controller"):
        lines.append(f"{n}: {p[n][2]:.1f} mm deep, {d['usable_depth'] - p[n][2]:.1f} mm to the lid")
    return lines


if __name__ == "__main__":
    from build123d import export_step, export_stl
    probs = fit_check()
    for line in report():
        print(line)
    if probs:
        print("FIT PROBLEMS:")
        for pr in probs:
            print("  " + pr)
    else:
        print("fit check: all parts clear by 3 mm and sit inside the enclosure")
    part = build()
    out = Path(__file__).resolve().parents[1]
    export_step(part, str(out / "step" / "thermabrick-controller-enclosure.step"))
    export_stl(part, str(out / "stl" / "thermabrick-controller-enclosure.stl"))
    raise SystemExit(1 if probs else 0)
