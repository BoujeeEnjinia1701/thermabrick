"""ThermaBrick product appearance model (build123d), TRL 3.

Finished-product look for photoreal renders: the insulated drum with a galvanized jacket in three
lapped rows, riveted seams, a teal top trim ring and a dark kick plinth, a name plate and HOT
SURFACE warning labels; an 80 deg cut sector through the jacket, stone wool, AES blanket, drum
and sand bed that shows two heater wells split open with their glowing cartridge heaters, a
U-tube and the layered base (stone wool board, insulating firebrick, AES board); the annular
inlet plenum with its servo-driven inlet damper and intake grille; the heater junction box on
the jacket top; the black 4 in hot outlet duct in a perforated guard sleeve, rising and turning
down as a heat trap into the mixing tee with its balancing damper; the EC inline fan on a wall
bracket; the insulated flexible supply duct into the wall; and the wall-mounted control
enclosure with its independent high-limit readout and a lit charge light. Context is a compact
patch of slab floor and back wall with surface conduit.
APPEARANCE MODEL ONLY: no tolerances, no fabrication detail. CONCEPT, NOT FOR FABRICATION.

Every main dimension and interface comes from PARAMS, derived() and build() in model.py
(same axes: origin at floor level on the drum axis, +Z up, front toward -Y). The duct run,
fan, junction box and control enclosure are not in model.py; their positions here are an
appearance layout, recorded as proposed in docs/REVIEW.md, session 2026-09-26.

    from product_model import product_parts
    for p in product_parts(): print(p["name"], p["group"], p["material"])
"""
import sys
from math import cos, sin, radians
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build123d import (Axis, Box, Compound, Cylinder, Plane, Polygon, Pos, Rot, Solid, Sphere, Vector,
                       extrude, fillet)
from model import PARAMS, derived, build

TITLE = "ThermaBrick: sand thermal battery for solar space heating"

RENDER_VIEWS = [
    {"name": "hero", "groups": ["shell", "internal", "accessory", "context"], "explode": False,
     "el": 30, "az": -40,
     "note": "Product render from the front right and above (about 30 deg elevation); cut sector at front "
             "shows the sand bed and glowing heaters, hot outlet duct, mixing tee and fan at right, "
             "control enclosure on the wall behind"},
    {"name": "exploded", "groups": ["shell", "internal", "accessory"], "explode": True, "el": 28, "az": -55,
     "note": "Exploded view from the front right and above (about 28 deg elevation): jacket with its stone "
             "wool wrap slid left and base layers drawn down; drum with sand, heater wells and U-tubes; lid, collector, inlet "
             "plenum and damper; hot duct, mixing tee, fan and supply duct; control enclosure"},
    {"name": "detail", "groups": ["shell", "internal"], "explode": False, "el": 22, "az": -38,
     "note": "Detail from the front right, slightly above (about 22 deg elevation): the cut sector through "
             "jacket, insulation, drum and sand, with two heater wells split open and a U-tube"},
]

# Appearance layout (not in model.py)
CUT = (268.0, 345.0)        # cut sector, deg from +X toward +Y; clears the inlet collar at 0 deg
DUCT_ANG = 35.0             # hot duct run heads this way from the outlet, then drops to the tee
DUCT_R = 800.0              # radius of the drop, mixing tee and fan from the drum axis
DUCT_TOP = 1640.0           # centreline of the horizontal hot run
TEE_Z = 1150.0              # mixing tee centre
FAN_Z = (765.0, 995.0)      # fan body bottom and top
FLEX_Z = 380.0              # supply duct horizontal run into the wall
WALL_Y = 900.0              # inside face of the back wall
JBOX = (120.0, 430.0)       # heater junction box, angle and radius on the jacket top
ENCL = (-480.0, 1560.0)     # control enclosure centre X and Z on the back wall
FLOOR = (-780.0, 1080.0, -720.0)   # floor patch x0, x1, y0 (y1 is the wall)

# Colours (restrained product palette; kit accent)
C_JACKET = "#C4CAD0"
C_ACCENT = "#0F766E"
C_PLINTH = "#2B2F36"
C_STEEL = "#3F454D"
C_BLACK = "#24272C"
C_SAND = "#E3C68E"
C_AES = "#F2EFE8"
C_MW = "#A8A48A"
C_IFB = "#E4D6BC"
C_HEAT = "#FF7A2F"
C_BEAD = "#EEEAE0"
C_METAL = "#B8BEC6"
C_DARK = "#2B2F36"
C_LABEL = "#F4F4F2"
C_WARN = "#F2C21B"
C_INK = "#1C1F24"
C_FLEX = "#C9CDD2"
C_ENCL = "#E4E6E9"
C_LED_G = "#22C55E"
C_LED_A = "#6E5315"
C_LED_R = "#F04438"
C_FLOOR = "#D9D6D0"
C_WALL = "#E6E3DE"


def _fillet_try(shape, edges, radii):
    """Fillet `edges` with the first radius that gives a valid solid; else return the input."""
    edges = list(edges)
    if not edges:
        return shape
    for r in radii:
        try:
            out = fillet(edges, r)
            if out.is_valid and out.volume > 0:
                return out
        except Exception:
            pass
    return shape


def _box(cx, cy, cz, sx, sy, sz):
    return Pos(cx, cy, cz) * Box(sx, sy, sz)


def _zcyl(x, y, z, r, h):
    return Pos(x, y, z) * Cylinder(r, h)


def _ycyl(x, y, z, r, h):
    return Pos(x, y, z) * Rot(90, 0, 0) * Cylinder(r, h)


def _xcyl(x, y, z, r, h):
    return Pos(x, y, z) * Rot(0, 90, 0) * Cylinder(r, h)


def _ring(r_o, r_i, z0, h):
    return Pos(0, 0, z0 + h / 2) * (Cylinder(r_o, h) - Cylinder(r_i, h + 1))


def _pipe(points, r):
    """Round tube through `points` with spherical joints (clean bends)."""
    out = None
    for a, c in zip(points, points[1:]):
        a, c = Vector(*a), Vector(*c)
        d = c - a
        seg = Solid.make_cylinder(r, d.length, Plane(origin=a, z_dir=d.normalized()))
        out = seg if out is None else out + seg
    for q in points[1:-1]:
        out += Pos(*q) * Sphere(r)
    return out


def _union(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


def _polar(r, deg):
    return r * cos(radians(deg)), r * sin(radians(deg))


def _wedge(a0, a1, z0, z1):
    """Sector between angles a0 and a1 (a1 - a0 < 180 deg), from z0 to z1."""
    h, zc = z1 - z0, (z0 + z1) / 2
    b1 = Rot(0, 0, a0 + 90) * Pos(2000, 0, zc) * Box(4000, 6000, h)
    b2 = Rot(0, 0, a1 - 90) * Pos(2000, 0, zc) * Box(4000, 6000, h)
    return b1 & b2


def _circles(s, keep):
    """Circular edges of `s` whose radius and centre height pass keep(r, z)."""
    out = []
    for e in s.edges():
        try:
            r = e.radius
        except Exception:
            continue
        if keep(r, e.center().Z):
            out.append(e)
    return out


def _top(s):
    return s.faces().sort_by(Axis.Z)[-1].edges()


def _bottom(s):
    return s.faces().sort_by(Axis.Z)[0].edges()


def _front(s):
    return s.faces().sort_by(Axis.Y)[0].edges()


def _warn_marks(w, h):
    """Warning-label print in a local YZ frame centred on the label: triangle outline and heat waves."""
    s = h * 0.42
    cz = h * 0.12
    tri = [(-w * 0.5 + 6, cz - s / 2), (-w * 0.5 + 6 + s * 1.15, cz - s / 2), (-w * 0.5 + 6 + s * 0.575, cz + s / 2)]
    inner = [(tri[0][0] + 3.2, tri[0][1] + 1.8), (tri[1][0] - 3.2, tri[1][1] + 1.8), (tri[2][0], tri[2][1] - 3.8)]
    outline = extrude(Plane.YZ * Polygon(*tri), amount=10) - extrude(Plane.YZ * Polygon(*inner), amount=12)
    outline = Pos(-5, 0, 0) * outline
    tx = tri[2][0]
    waves = _union([_box(0, tx + dy, cz - s * 0.08, 10, 1.4, s * 0.34) for dy in (-3.2, 0, 3.2)])
    text = _union([_box(0, w * 0.18, cz + s * 0.22, 10, w * 0.46, s * 0.2),
                   _box(0, w * 0.18, cz - s * 0.14, 10, w * 0.46, s * 0.2),
                   _box(0, 0, -h * 0.32, 10, w * 0.84, h * 0.08),
                   _box(0, -w * 0.08, -h * 0.44, 10, w * 0.68, h * 0.06)])
    return outline + waves + text


def _curved(theta, r0, t, zc, w, h, local):
    """Intersect `local` (built with radial = +X, tangential = +Y about the origin, z about zc) with a
    cylindrical shell r0..r0+t, then turn it to face `theta`."""
    shell = Pos(0, 0, zc) * (Cylinder(r0 + t, h + 2) - Cylinder(r0, h + 4))
    return (Rot(0, 0, theta) * (Pos(r0, 0, zc) * local)) & shell


def _curved_label(theta, r0, zc, w, h):
    plate = _curved(theta, r0, 0.5, zc, w, h, Box(200, w, h))
    ink = _curved(theta, r0 + 0.5, 0.35, zc, w, h, _warn_marks(w, h))
    return plate, ink


def product_parts(P=PARAMS):
    D = derived(P)
    _, M = build(parts=True)
    out = []

    def add(name, shape, color, material, bom, group, explode):
        out.append({"name": name, "shape": shape, "color": color, "material": material,
                    "bom": bom, "group": group, "explode": tuple(float(v) for v in explode)})

    rj, rji = D["jacket_r_o"], D["jacket_r_i"]
    zt = D["jacket_top_z"]
    ztc = zt + P["jacket_t"]                        # top of the jacket cap
    zp = ztc + P["inlet_plenum_h"]                  # top of the inlet plenum
    cut = _wedge(CUT[0], CUT[1], -1.0, zp + 1.0)
    cut_hi = _wedge(CUT[0], CUT[1], -1.0, zt - 1.0)  # below the jacket cap for the outer trims

    # Explode directions for the az -55 view: screen right is the 35 deg ray, screen left 215 deg
    L = (cos(radians(215)), sin(radians(215)))
    R = (cos(radians(35)), sin(radians(35)))
    EJ = (1400 * L[0], 1400 * L[1], 0)             # jacket and its trims slide left
    EM = EJ                                        # stone wool goes with the jacket, seen through the cut

    # ------------------------------------------------------------ jacket (BOM 25, 26)
    jacket = M["jacket"] - cut
    add("Galvanized jacket", jacket, C_JACKET, "metal", 25, "shell", EJ)

    rows = (zt / 3, 2 * zt / 3)
    laps = _union([_ring(rj + 1.2, rj - 0.2, z - 15, 30) for z in rows])
    laps += _curved(250.0, rj - 0.2, 1.4, zt / 2, 30, zt - 2, Box(200, 30, zt))  # vertical lap at 0 deg
    laps -= cut
    add("Jacket lap seams", laps, C_JACKET, "metal", 25, "shell", EJ)

    riv = []
    for z in rows:
        for k in range(24):
            a = 7.5 + 15 * k
            if CUT[0] - 4 < a < CUT[1] + 4:
                continue
            x, y = _polar(rj + 1.2, a)
            riv.append(Pos(x, y, z) * Rot(0, 0, a) * Rot(0, 90, 0) * Cylinder(4.0, 2.4))
    for k in range(11):
        x, y = _polar(rj + 1.4, 250.0)
        riv.append(Pos(x, y, 60 + k * (zt - 120) / 10) * Rot(0, 0, 250) * Rot(0, 90, 0) * Cylinder(4.0, 2.4))
    add("Jacket rivets", Compound(riv), C_METAL, "metal", 26, "shell", EJ)

    bead = _ring(rj + 3.0, rj - 6.0, zt - 16, 20)
    bead = _fillet_try(bead, _circles(bead, lambda r, z: r > rj + 1), [3.0, 2.0, 1.0])
    bead -= cut
    add("Top trim ring", bead, C_ACCENT, "painted", 26, "shell", EJ)

    plinth = _ring(rj + 4.0, rj - 4.0, 0, 60)
    plinth = _fillet_try(plinth, _circles(plinth, lambda r, z: r > rj + 1 and z > 30), [4.0, 3.0, 2.0])
    plinth -= cut_hi
    add("Kick plinth", plinth, C_PLINTH, "rubber", 26, "shell", EJ)

    # name plate and HOT SURFACE labels on the jacket (thin raised parts)
    np_ = _curved(15.0, rj + 1.3, 0.6, 1060.0, 150, 34, Box(200, 150, 34))
    add("Name plate", np_, C_ACCENT, "painted", 26, "shell", EJ)
    npi = _curved(15.0, rj + 1.9, 0.3, 1060.0, 150, 34,
                  _box(0, -18, 3, 10, 96, 9) + _box(0, 42, 3, 10, 14, 9) + _box(0, 0, -9, 10, 124, 3))
    add("Name plate print", npi, C_LABEL, "paper", 26, "shell", EJ)
    wl, wi = _curved_label(358.0, rj + 1.3, 1060.0, 96, 64)
    add("HOT SURFACES INSIDE label", wl, C_WARN, "paper", 26, "shell", EJ)
    add("HOT SURFACES INSIDE label print", wi, C_INK, "paper", 26, "shell", EJ)

    tl = _box(0, 0, 0, 96, 64, 0.5)
    tx, ty = _polar(470.0, 205.0)
    top_lab = Pos(tx, ty, ztc + 0.25) * Rot(0, 0, 205 + 90) * tl
    top_ink = Pos(tx, ty, ztc + 0.65) * Rot(0, 0, 205 + 90) * Rot(0, 0, 90) * (
        Rot(0, -90, 0) * _warn_marks(96, 64) & Box(200, 200, 0.3))
    add("HOT OUTLET label", top_lab, C_WARN, "paper", 26, "shell", EJ)
    add("HOT OUTLET label print", top_ink, C_INK, "paper", 26, "shell", EJ)

    # ------------------------------------------------------------ insulation (BOM 19 to 23)
    ins = M["insulation"] - cut
    zb = D["base_h"]
    zaes = D["top_ins_z0"] + P["ins_top_aes"]
    aes_reg = Pos(0, 0, (zb + zaes) / 2) * Cylinder(D["drum_r_o"] + P["ins_side_aes"], zaes - zb)
    aes_reg -= Pos(0, 0, (zb + D["top_ins_z0"]) / 2) * Cylinder(D["drum_r_o"] + 0.01, D["top_ins_z0"] - zb)
    aes_reg += Pos(0, 0, D["sand_top_z"] + P["ins_top_aes"] / 2) * Cylinder(D["drum_r_i"], P["ins_top_aes"])
    aes = ins & aes_reg
    mw = ins - aes_reg
    add("AES fiber blanket, hot face", aes, C_AES, "fabric", 19, "internal", (0, 0, 0))
    add("Stone wool wrap and top batts", mw, C_MW, "fabric", 22, "internal", EM)

    base_layers = [("Stone wool base board", 0.0, P["base_mw"], C_MW, "fabric", 23, -620),
                   ("Insulating firebrick course", P["base_mw"], P["base_ifb"], C_IFB, "paper", 21, -440),
                   ("AES fiber board", P["base_mw"] + P["base_ifb"], P["base_aes"], C_AES, "fabric", 20, -260)]
    for nm, z0, h, col, mat, bom, dz in base_layers:
        s = Pos(0, 0, z0 + h / 2) * Cylinder(rji, h) - cut
        if nm.startswith("Insulating"):
            # brick joints on the cut faces and top (texture)
            for k in range(-3, 4):
                s -= Rot(0, 0, CUT[0]) * _box(k * 114 + 57, 0, z0 + h / 2, 3, 4, h + 2)
                s -= Rot(0, 0, CUT[1]) * _box(k * 114 + 57, 0, z0 + h / 2, 3, 4, h + 2)
        add(nm, s, col, mat, bom, "internal", (0, 0, dz))

    # ------------------------------------------------------------ drum, lid, sand (BOM 1, 2)
    add("55 gal steel drum", M["drum"] - cut, C_STEEL, "metal", 1, "internal", (0, 0, 0))
    add("Drum lid and closing ring", M["lid"] - cut, C_STEEL, "metal", 1, "internal", (0, 0, 520))
    add("Sand bed, 210 kg", M["sand"] - cut, C_SAND, "paper", 2, "internal", (0, 0, 0))

    # ------------------------------------------------------------ heater wells and heaters (BOM 3 to 5)
    cam = radians(-40.0)
    cv = (cos(cam), sin(cam))
    wells, heaters, leads = [], [], []
    w_z0 = D["floor_z"] + P["well_floor_gap"]
    h_w = D["well_top_z"] - w_z0
    for i in range(D["n_heaters"]):
        a = 360 / P["n_per_ring"] * (i % P["n_per_ring"])
        x, y = _polar(P["heater_rings"][i // P["n_per_ring"]], a)
        well = _zcyl(x, y, w_z0 - 6 + P["well_cap_h"] / 2, P["well_cap_od"] / 2, P["well_cap_h"])
        well += _zcyl(x, y, w_z0 + h_w / 2, P["well_od"] / 2, h_w)
        well -= _zcyl(x, y, w_z0 + 6 + h_w / 2, P["well_id"] / 2, h_w)
        if CUT[0] < a < CUT[1]:
            # split open on the side facing the viewer, so the heater shows
            half = Pos(x, y, w_z0 + h_w / 2) * Rot(0, 0, -40) * Pos(100, 0, 0) * Box(200, 200, h_w + 40)
            well -= half
            leads.append(_zcyl(x + 3, y, (w_z0 + 6 + P["heater_len"] + D["well_top_z"]) / 2, 2.2,
                               D["well_top_z"] - w_z0 - 6 - P["heater_len"]))
            leads.append(_zcyl(x - 3, y, (w_z0 + 6 + P["heater_len"] + D["well_top_z"]) / 2, 2.2,
                               D["well_top_z"] - w_z0 - 6 - P["heater_len"]))
        wells.append(well)
        hz0 = w_z0 + 6
        ht = _zcyl(x, y, hz0 + P["heater_len"] / 2, P["heater_d"] / 2, P["heater_len"])
        heaters.append(ht)
    add("Heater wells, 3/4 in black steel", Compound(wells), C_BLACK, "metal", 4, "internal", (0, 0, 0))
    add("Cartridge heaters (charging, lit)", Compound(heaters), C_HEAT, "emissive", 3, "internal", (0, 0, 0))
    add("Heater leads, ceramic beaded", Compound(leads), C_BEAD, "plastic", 3, "internal", (0, 0, 0))

    add("U-tube heat exchanger", M["utubes"], "#26292E", "metal", 6, "internal", (0, 0, 0))
    add("Hot collector and outlet", M["collector"] - cut, "#1F2328", "metal", 10, "internal", (0, 0, 820))

    # ------------------------------------------------------------ inlet plenum and damper (BOM 14, 15, 25)
    add("Inlet plenum and collar", M["inlet_plenum"] - cut, C_JACKET, "metal", 25, "shell", (0, 0, 1180))
    pl_ro = P["leg_outer_r"] + 45
    cz = ztc + P["inlet_plenum_h"] / 2
    r4 = P["outlet_d"] / 2
    x0 = pl_ro - 5 + 120                            # end of the inlet collar
    EI = (0, 0, 1180)
    damp = _xcyl(x0 + 40, 0, cz, r4 + 1.5, 80)
    damp += _xcyl(x0 + 4, 0, cz, r4 + 4, 8) + _xcyl(x0 + 76, 0, cz, r4 + 4, 8)
    add("Inlet damper", damp, C_JACKET, "metal", 14, "accessory", EI)
    servo = _box(x0 + 40, 0, cz + r4 + 22, 42, 22, 40)
    servo = _fillet_try(servo, servo.edges().filter_by(Axis.Z), [3.0, 2.0])
    servo += _box(x0 + 40, 0, cz + r4 + 1, 60, 30, 4)
    add("Inlet damper servo", servo, C_DARK, "plastic", 15, "accessory", EI)
    sl = _box(x0 + 40, -11.3, cz + r4 + 26, 26, 0.4, 12)
    add("Servo label", sl, C_ACCENT, "painted", 15, "accessory", EI)
    bell = _xcyl(x0 + 95, 0, cz, r4 + 12, 30)
    bell = _fillet_try(bell, [e for e in bell.edges() if e.center().X > x0 + 100], [8.0, 5.0, 3.0])
    bell -= _xcyl(x0 + 95, 0, cz, r4 - 1, 40)
    add("Intake bell mouth", bell, C_JACKET, "metal", 14, "accessory", EI)
    grille = _xcyl(x0 + 104, 0, cz, r4 - 0.5, 3)
    for k in range(-4, 5):
        grille -= _box(x0 + 104, k * 10, cz, 5, 5, 2 * r4)
    add("Intake grille", grille, C_DARK, "plastic", 14, "accessory", EI)

    # ------------------------------------------------------------ heater junction box (BOM 42)
    ja, jr = JBOX
    jx, jy = _polar(jr, ja)
    EB = (EJ[0], EJ[1], 380)
    jb = _box(jx, jy, ztc + 45, 150, 150, 90)
    jb = _fillet_try(jb, jb.edges().filter_by(Axis.Z), [6.0, 4.0])
    add("Heater junction box", jb, C_METAL, "metal", 42, "shell", EB)
    jl = _box(jx, jy, ztc + 95, 154, 154, 10)
    jl = _fillet_try(jl, jl.edges().filter_by(Axis.Z), [7.0, 5.0])
    jl = _fillet_try(jl, _top(jl), [2.0, 1.0])
    add("Junction box lid", jl, "#AEB4BB", "metal", 42, "shell", (EB[0], EB[1], 460))
    js = Compound([_zcyl(jx + sx * 62, jy + sy * 62, ztc + 100.8, 4.0, 1.6)
                   for sx in (-1, 1) for sy in (-1, 1)])
    add("Junction box lid screws", js, C_DARK, "metal", 42, "shell", (EB[0], EB[1], 470))
    vl = _box(jx, jy - 75.3, ztc + 45, 90, 0.5, 44)
    vi = Pos(jx, jy - 75.8, ztc + 45) * Rot(0, 0, -90) * _warn_marks(90, 44) & _box(jx, jy - 75.8, ztc + 45, 200, 0.3, 200)
    add("DANGER 240 V label", vl, C_WARN, "paper", 42, "shell", EB)
    add("DANGER 240 V label print", vi, C_INK, "paper", 42, "shell", EB)
    jg = _ycyl(jx, jy + 81, ztc + 50, 11.0, 12)
    add("Junction box gland", jg, C_DARK, "plastic", 42, "shell", EB)

    # ------------------------------------------------------------ hot duct, tee, fan (BOM 12 to 18)
    A = DUCT_ANG
    ED = (950 * R[0], 950 * R[1], 420)            # duct run lifts and slides right
    rot = Rot(0, 0, A)
    X1 = DUCT_R
    oz = D["overall_h"]
    hot = _pipe([(0, 0, oz - 6), (0, 0, DUCT_TOP), (X1, 0, DUCT_TOP), (X1, 0, TEE_Z + 118)], r4 + 1.0)
    add("Hot outlet duct, 4 in black stovepipe", rot * hot, C_BLACK, "metal", 12, "accessory", ED)
    bands = [_zcyl(0, 0, oz + 20, r4 + 3, 14), _xcyl(X1 / 2, 0, DUCT_TOP, r4 + 3, 14),
             _zcyl(X1, 0, TEE_Z + 200, r4 + 3, 14)]
    add("Stovepipe crimp joints", rot * _union(bands), "#34383E", "metal", 12, "accessory", ED)

    # perforated guard sleeve over the hot run and drop
    rs = r4 + 28
    sh = _xcyl((130 + X1 - 110) / 2, 0, DUCT_TOP, rs, X1 - 240) - _xcyl((130 + X1 - 110) / 2, 0, DUCT_TOP, rs - 2.5, X1)
    holes = []
    for k in range(int((X1 - 280) / 32)):
        xh = 160 + 32 * k
        for o in (-40, 0, 40):
            holes.append(_zcyl(xh + (16 if o else 0), o, DUCT_TOP, 7.0, 3 * rs))
            holes.append(_ycyl(xh + (16 if o else 0), 0, DUCT_TOP + o, 7.0, 3 * rs))
    sh -= Compound(holes)
    zs0, zs1 = TEE_Z + 150, DUCT_TOP - 110
    sv = _zcyl(X1, 0, (zs0 + zs1) / 2, rs, zs1 - zs0) - _zcyl(X1, 0, (zs0 + zs1) / 2, rs - 2.5, zs1 - zs0 + 2)
    holes = []
    for k in range(int((zs1 - zs0 - 150) / 32)):
        zh = zs0 + 20 + 32 * k
        for o in (-40, 0, 40):
            holes.append(_xcyl(X1, o, zh + (16 if o else 0), 7.0, 3 * rs))
            holes.append(_ycyl(X1 + o, 0, zh + (16 if o else 0), 7.0, 3 * rs))
    sv -= Compound(holes)
    add("Perforated guard sleeve", rot * (sh + sv), C_METAL, "metal", 12, "accessory", ED)
    # HOT SURFACE band on the drop, facing the viewer (local angle 285 deg)
    loc_face = -40.0 - A
    zlab = zs1 - 55
    pl, pi_ = _curved_label(loc_face, rs, zlab, 84, 60)
    add("HOT SURFACE label", rot * (Pos(X1, 0, 0) * pl), C_WARN, "paper", 12, "accessory", ED)
    add("HOT SURFACE label print", rot * (Pos(X1, 0, 0) * pi_), C_INK, "paper", 12, "accessory", ED)

    # mixing tee with the balancing damper on its room-air branch
    tee = _zcyl(X1, 0, TEE_Z, r4 + 3, 240)
    tee += _ycyl(X1, -110, TEE_Z, r4 + 3, 220)
    add("Mixing tee", rot * tee, C_BLACK, "metal", 13, "accessory", ED)
    bd = _ycyl(X1, -175, TEE_Z, r4 + 7, 60)
    bd -= _ycyl(X1, -175, TEE_Z, r4 + 3, 70)
    add("Bypass balancing damper", rot * bd, C_JACKET, "metal", 16, "accessory", ED)
    lever = _box(X1, -175, TEE_Z + r4 + 14, 12, 12, 16) + _box(X1 + 34, -175, TEE_Z + r4 + 24, 76, 6, 6)
    lever += _xcyl(X1 + 74, -175, TEE_Z + r4 + 24, 7, 18)
    add("Damper lever", rot * lever, C_ACCENT, "painted", 16, "accessory", ED)
    bg = _ycyl(X1, -222, TEE_Z, r4 + 2, 3)
    for k in range(-4, 5):
        bg -= _box(X1 + k * 10, -222, TEE_Z, 5, 6, 2 * r4)
    add("Room air grille", rot * bg, C_DARK, "plastic", 16, "accessory", ED)

    # EC inline fan, vertical in the drop below the tee
    EF = (ED[0], ED[1], ED[2] - 130)
    fz0, fz1 = FAN_Z
    fan = _zcyl(X1, 0, (fz0 + fz1) / 2, 118, fz1 - fz0)
    fan = _fillet_try(fan, fan.edges(), [22.0, 16.0, 10.0])
    for k in range(9):
        fan -= _ring(119, 115.5, fz0 + 45 + k * 17, 3.0) if k % 4 else _ring(119, 116.5, fz0 + 45 + k * 17, 1.5)
    add("EC inline fan", rot * fan, C_DARK, "plastic", 17, "accessory", EF)
    coll = _zcyl(X1, 0, fz1 + 18, r4 + 3, 36) + _zcyl(X1, 0, fz0 - 18, r4 + 3, 36)
    coll += _zcyl(X1, 0, fz1 + 3, 70, 8) + _zcyl(X1, 0, fz0 - 3, 70, 8)
    add("Fan collars", rot * coll, "#3A3F46", "plastic", 17, "accessory", EF)
    fr = _ring(119.4, 117.0, fz1 - 60, 10)
    add("Fan accent ring", rot * (Pos(X1, 0, 0) * fr), C_ACCENT, "painted", 17, "accessory", EF)
    flab = _curved(-40.0 - A, 118.5, 0.4, (fz0 + fz1) / 2 - 10, 70, 46, Box(200, 70, 46))
    add("Fan rating label", rot * (Pos(X1, 0, 0) * flab), C_LABEL, "paper", 17, "accessory", EF)
    led = _curved(-40.0 - A, 118.5, 2.0, fz1 - 30, 8, 8, Box(200, 8, 8))
    add("Fan run light (lit)", rot * (Pos(X1, 0, 0) * led), C_LED_G, "emissive", 17, "accessory", EF)
    fx, fy = _polar(X1, A)
    zfc = (fz0 + fz1) / 2
    clamp = _ring(126, 119.5, zfc - 15, 30)
    clamp = Pos(fx, fy, 0) * clamp
    clamp += _box(fx - 60, (fy + 120 + WALL_Y) / 2, zfc, 10, WALL_Y - fy - 120, 30)
    clamp += _box(fx + 60, (fy + 100 + WALL_Y) / 2, zfc, 10, WALL_Y - fy - 100, 30)
    clamp += _box(fx, WALL_Y - 3, zfc, 160, 6, 70)
    add("Fan wall bracket", clamp, "#5B6168", "painted", 17, "accessory", EF)

    # insulated flexible supply duct into the wall (ribbed)
    EX = (ED[0], ED[1] + 120, ED[2] - 260)
    rf = 64.0
    zf0 = fz0 - 36
    flex = _pipe([(fx, fy, zf0), (fx, fy, FLEX_Z), (fx, WALL_Y - 40, FLEX_Z)], rf)
    ribs = []
    n1 = int((zf0 - FLEX_Z - rf) / 26)
    for k in range(n1):
        ribs.append(_zcyl(fx, fy, zf0 - 16 - 26 * k, rf + 2.2, 6))
    n2 = int((WALL_Y - 40 - fy - rf) / 26)
    for k in range(n2):
        ribs.append(_ycyl(fx, fy + rf + 12 + 26 * k, FLEX_Z, rf + 2.2, 6))
    flex = flex + Compound(ribs)
    add("Insulated flexible supply duct", flex, C_FLEX, "fabric", 18, "accessory", EX)
    clampf = _zcyl(fx, fy, zf0 - 8, rf + 4, 14)
    add("Duct clamp", clampf, C_METAL, "metal", 18, "accessory", EX)

    # ------------------------------------------------------------ control enclosure (BOM 27 to 41)
    ex, ez = ENCL
    EE = (-700, -950, 250)
    ew, eh, ed = 300.0, 250.0, 150.0
    ey0 = WALL_Y - ed                               # front face of the body
    body = _box(ex, WALL_Y - ed / 2, ez, ew, ed, eh)
    body = _fillet_try(body, body.edges().filter_by(Axis.Y), [6.0, 4.0])
    body -= _box(ex, ey0 + 3, ez, ew - 8, 8, eh - 8)
    add("Control enclosure", body, C_ENCL, "painted", 41, "accessory", EE)
    door = _box(ex, ey0 - 2, ez, ew - 10, 6, eh - 10)
    door = _fillet_try(door, door.edges().filter_by(Axis.Y), [5.0, 3.0])
    door = _fillet_try(door, _front(door), [1.5, 1.0])
    add("Enclosure door", door, C_ENCL, "painted", 41, "accessory", EE)
    hinge = _zcyl(ex - ew / 2 + 2, ey0 - 3, ez + 70, 5, 40) + _zcyl(ex - ew / 2 + 2, ey0 - 3, ez - 70, 5, 40)
    add("Door hinges", hinge, C_METAL, "metal", 41, "accessory", EE)
    latch = _ycyl(ex + ew / 2 - 25, ey0 - 7, ez, 11, 6)
    latch += _box(ex + ew / 2 - 25, ey0 - 12, ez, 6, 6, 18)
    add("Door latch", latch, C_DARK, "plastic", 41, "accessory", EE)
    epl = _box(ex, ey0 - 5.2, ez + eh / 2 - 26, 150, 0.5, 16)
    add("Enclosure name plate", epl, C_ACCENT, "painted", 41, "accessory", EE)
    epi = _box(ex - 20, ey0 - 5.6, ez + eh / 2 - 26, 90, 0.3, 5) + _box(ex + 52, ey0 - 5.6, ez + eh / 2 - 26, 24, 0.3, 5)
    add("Enclosure name plate print", epi, C_LABEL, "paper", 41, "accessory", EE)
    # independent high limit, 1/16 DIN
    hlx, hlz = ex - 60, ez + 20
    hl = _box(hlx, ey0 - 9, hlz, 56, 10, 56)
    hl = _fillet_try(hl, hl.edges().filter_by(Axis.Y), [3.0, 2.0])
    add("High-limit controller bezel", hl, C_INK, "plastic", 35, "accessory", EE)
    hg = _box(hlx, ey0 - 14.2, hlz + 8, 44, 0.5, 20)
    add("High-limit display glass", hg, "#0E1216", "screen", 35, "accessory", EE)
    digits = _union([_box(hlx - 15 + 10 * k, ey0 - 14.6, hlz + 8, 7, 0.3, 14) for k in range(4)])
    add("High-limit readout (lit)", digits, C_LED_R, "emissive", 35, "accessory", EE)
    keys = _union([_box(hlx - 15 + 10 * k, ey0 - 14.4, hlz - 13, 7, 1.0, 5) for k in range(4)])
    add("High-limit keys", keys, "#4B5563", "rubber", 35, "accessory", EE)
    # lights and switch
    lx, lz = ex + 40, ez + 32
    for k, (col, mat, nm) in enumerate([(C_LED_G, "emissive", "Charge light, green (lit)"),
                                        (C_LED_A, "plastic", "Discharge light, amber"),
                                        ("#5E1C1C", "plastic", "Fault light, red")]):
        bz_ = lz - 30 * k
        bez = _ycyl(lx, ey0 - 7, bz_, 9, 4) - _ycyl(lx, ey0 - 9, bz_, 6.5, 4)
        add(f"{nm} bezel", bez, C_METAL, "metal", 41, "accessory", EE)
        dome = _ycyl(lx, ey0 - 7, bz_, 6.4, 3) + Pos(lx, ey0 - 9, bz_) * Sphere(5.5)
        dome &= _box(lx, ey0 - 9, bz_, 14, 6, 14)
        add(nm, dome, col, mat, 41, "accessory", EE)
        add(f"{nm} legend", _box(lx + 30, ey0 - 5.2, bz_, 30, 0.3, 4), C_INK, "paper", 41, "accessory", EE)
    wl2 = _box(ex + 60, ey0 - 5.2, ez - 78, 70, 0.5, 48)
    wi2 = Pos(ex + 60, ey0 - 5.6, ez - 78) * Rot(0, 0, -90) * _warn_marks(70, 48) \
        & _box(ex + 60, ey0 - 5.6, ez - 78, 200, 0.3, 200)
    add("DANGER 240 V label, enclosure", wl2, C_WARN, "paper", 41, "accessory", EE)
    add("DANGER 240 V label print, enclosure", wi2, C_INK, "paper", 41, "accessory", EE)
    gl = _union([_zcyl(ex + dx, WALL_Y - ed / 2, ez - eh / 2 - 8, 10, 16) for dx in (-80, 80)])
    gl += _xcyl(ex + ew / 2 + 8, WALL_Y - 40, ez - 40, 10, 16)
    add("Enclosure cable glands", gl, C_DARK, "plastic", 41, "accessory", EE)

    # ------------------------------------------------------------ context (not in the BOM)
    fx0, fx1, fy0 = FLOOR
    add("Floor slab patch", _box((fx0 + fx1) / 2, (fy0 + WALL_Y) / 2, -20, fx1 - fx0, WALL_Y - fy0, 40),
        C_FLOOR, "painted", None, "context", (0, 0, 0))
    wh = 1760.0
    add("Back wall patch", _box((fx0 + fx1) / 2, WALL_Y + 50, wh / 2 - 40, fx1 - fx0, 100, wh + 40),
        C_WALL, "paper", None, "context", (0, 0, 0))
    wc = _box(fx, WALL_Y - 3, FLEX_Z, 200, 6, 200)
    wc = _fillet_try(wc, wc.edges().filter_by(Axis.Y), [6.0, 4.0])
    wc += _ycyl(fx, WALL_Y - 20, FLEX_Z, rf + 6, 40)
    add("Wall duct collar (to room register)", wc, C_ENCL, "painted", 18, "context", (0, 0, 0))
    rc = 10.0
    cz0 = ztc + 50
    cond = _pipe([(jx, jy + 87, cz0), (jx, WALL_Y - 30, cz0), (jx, WALL_Y - 30, ez - 40),
                  (ex + ew / 2 + 16, WALL_Y - 30, ez - 40)], rc)
    cond += _pipe([(ex - 80, WALL_Y - ed / 2, ez - eh / 2 - 16), (ex - 80, WALL_Y - ed / 2, ez - eh / 2 - 60),
                   (ex - 80, WALL_Y - 20, ez - eh / 2 - 100), (ex - 80, WALL_Y - 20, 1.0)], rc)
    cond += _pipe([(ex + 80, WALL_Y - ed / 2, ez - eh / 2 - 16), (ex + 80, WALL_Y - ed / 2, ez - eh / 2 - 60),
                   (ex + 80, WALL_Y - 20, ez - eh / 2 - 100), (fx - 40, WALL_Y - 20, ez - eh / 2 - 100),
                   (fx - 40, WALL_Y - 20, zfc + 60)], 6.0)
    add("Surface conduit", cond, C_METAL, "metal", 40, "context", (0, 0, 0))
    straps = Compound([_box(x, WALL_Y - 12, z, 30, 24, 8) for (x, z) in
                       [(jx, 1500.0), (ex - 80, 900.0), (ex - 80, 400.0), (ex + 80 + 300, ez - eh / 2 - 100)]])
    add("Conduit straps", straps, C_METAL, "metal", 40, "context", (0, 0, 0))
    return out


if __name__ == "__main__":
    for p in product_parts():
        s = p["shape"]
        print(f"{p['name']:42s} {p['group']:9s} {p['material']:8s} valid={s.is_valid} vol={s.volume / 1000:9.2f} cm3")
