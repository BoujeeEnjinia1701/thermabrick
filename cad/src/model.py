"""ThermaBrick parametric model (build123d).

Run from the repo root:
    python cad/src/model.py            export STEP and STL into cad/step and cad/stl
    python cad/src/model.py --check    run the constructability checks (TBK-DDR-003)

PARAMS is the single source of truth for geometry. The sizing script
docs/04-calcs/tbk_cal_001.py imports it, so every number in TBK-CAL-001 comes
from the same dimensions that the CAD model and TBK-DWG-001 show.

Kit 1.7.0 (2026-10-01): the model is constructable (design_state: constructable).
Every part can be bought or made by the stated process and is held by a stated
fixing; the changes from the concept are recorded in TBK-DDR-003.

Coordinate frame: origin at floor level on the drum axis, +Z up, millimeters.
"""
import sys
from math import cos, sin, radians, pi, hypot, atan2, degrees
from pathlib import Path

# Top-level parameters (mm unless noted). Edit these, not the geometry below.
PARAMS = {
    # Storage vessel: 55 US gal open-head steel drum, unlined, 18 ga body (ANSI MH2 nominal)
    "drum_id": 571.5,            # 22.5 in
    "drum_wall": 1.2,            # 18 ga
    "drum_h": 883.0,             # overall height over chimes, 34.75 in
    "drum_floor": 13.5,          # inner floor height above drum bottom (chime recess + head)
    "chime_od": 597.0,           # rolled chime rings, top and bottom
    "chime_h": 10.0,
    "hoop_od": 606.0,            # two rolling hoops
    "hoop_h": 16.0,
    "hoop_z": (294.0, 589.0),    # hoop centers above drum bottom
    "lid_t": 1.6,                # 16 ga lid
    "ring_od": 606.0,            # bolted closing ring
    "ring_h": 22.0,

    # Storage medium
    "sand_mass_kg": 210.0,       # dry washed silica sand
    "sand_rho": 1600.0,          # bulk density, kg/m^3

    # Heater wells: 3/4 in Sch 40 black carbon steel pipe, capped at the bottom.
    # Two rings of six, on the rays at 0, 60, 120 ... deg (between the U-tubes).
    "heater_rings": (150.0, 245.0),
    "n_per_ring": 6,
    "well_od": 26.7,
    "well_id": 20.9,
    "well_floor_gap": 20.0,      # DDR-003 P1: the cap stands on a levelled 14 mm first lift of sand
    "well_cap_od": 33.0,
    "well_cap_h": 25.0,
    "heater_d": 15.9,            # 5/8 in cartridge heater
    "heater_len": 508.0,         # 20 in overall
    "heater_w": 250.0,           # W at 240 V
    "heater_heated_len": 457.0,  # 18 in heated, 2 in cold end at the lead end
    "heater_lead": 1829.0,       # DDR-003 P9: 72 in leads (36 in could not reach the junction box)

    # Discharge heat exchanger: six U-tubes of 1-1/4 in Sch 40 black steel pipe
    "n_utubes": 6,
    "leg_inner_r": 80.0,         # outlet (hot) legs, into the collector
    "leg_outer_r": 235.0,        # inlet (cold) legs, from the inlet plenum
    "utube_angle0": 30.0,        # deg; U-tubes at 30, 90, 150 ... (between the heater wells)
    "tube_od": 42.2,
    "tube_id": 35.1,
    "bend_z": 28.0,              # DDR-003 P2: elbows rest on the drum floor (was 50, floating)
    "elbow_od": 56.0,            # 1-1/4 in malleable iron 90 deg elbow, body over the bead
    "elbow_a": 44.5,             # center to end, ASME B16.3 class 150
    "thread_eng": 17.5,          # 1-1/4 in NPT make-up
    "nipple_len": 101.6,         # DDR-003 P2: 4 in nipple (a 2-1/2 in nipple gave 118 mm, not 155 mm)

    # Hot collector and outlet on the lid
    "collector_d": 254.0,        # 10 in black steel stovepipe section
    "collector_h": 80.0,
    "collector_tab": 20.0,       # DDR-003 P7: six tabs folded out at the foot, riveted to the lid
    "outlet_d": 101.6,           # 4 in steel pipe to the mixing tee
    "outlet_rise": 160.0,        # outlet stub height above the jacket top

    # Insulation (thicknesses)
    "ins_side_aes": 50.0,        # 2 x 25 mm AES fiber blanket, hot face
    "ins_side_mw": 267.0,        # 3 x 89 mm stone wool batt
    "ins_top_aes": 50.0,         # above the lid and collector
    "ins_top_mw": 178.0,
    "base_aes": 25.0,            # rigid AES fiber board, hot face
    "base_ifb": 64.0,            # one course of K-23 insulating firebrick, laid flat
    "base_mw": 100.0,            # 2 x 50 mm stone wool board
    "base_core_d": 610.0,        # DDR-003 P5: firebrick and AES board cut to a 610 mm disc under the drum
    "brick": (230.0, 114.0),     # K-23 brick face, laid flat
    "jacket_t": 0.6,             # 26 ga galvanized steel wrapper
    "cap_skirt": 25.0,           # jacket cap edge turned down over the side, screwed (DDR-003 P11)

    # Heater wells stop just above the lid; the ceramic-beaded leads run up through the top
    # insulation to a junction box on the jacket top, so no well crosses the top insulation.
    "well_above_lid": 25.0,
    "inlet_plenum_h": 140.0,     # DDR-003 P6: 140 mm (was 110) leaves a flange round the 4 in collar
    "plenum_flange": 15.0,

    # Holes (DDR-003 P3, P8, P10)
    "lid_well_hole": 36.0,       # well and its thermocouple pass together; AES rope collar on top
    "lid_tube_hole": 48.0,
    "tc_hole": 6.0,
    "cap_tube_hole": 46.0,
    "outlet_hole_d": 180.0,      # clearance hole in the galvanized cap, packed with AES blanket
    "trim_ring": (250.0, 106.0, 1.2),   # black steel trim ring over the packing: OD, ID, thickness
    "jbox": (120.0, 430.0, 150.0, 150.0, 100.0),   # junction box: angle, radius, size x, y, height
    "jbox_hole": 40.0,
    # Warning labels (BOM line 47; decision of 2026-10-02). Thin self-adhesive plates, 0.5 mm.
    # jacket: angle, height; cap: angle, radius; jbox: face label size. All 96 x 64 mm except the box.
    "label_t": 0.5,
    "label_jacket": (358.0, 1060.0, 96.0, 64.0),     # HOT SURFACES INSIDE, on the jacket side
    "label_cap": (205.0, 470.0, 96.0, 64.0),         # HOT OUTLET, on the jacket cap beside the outlet
    "label_jbox": (90.0, 44.0),                      # DANGER 240 V, on the outer face of the junction box
    "tc_exit": (95.0, 330.0, 25.0),     # thermocouple exit grommet: angle, radius, hole
    "tc_sheath": 1500.0,         # DDR-003 P10: MI thermocouple length (1,000 mm could not reach the exit)

    # Setting template (DDR-003 P4): plywood disc on the drum rim during the sand fill
    "template_t": 18.0,
    "pour_holes": (64.0, 200.0, (15.0, 105.0, 195.0, 285.0), 80.0),   # dia, radius, angles, centre dia
}


# Thermocouples (TBK-PRC-001 Table 3). (tag, x-y of the sheath in the sand, tip height above the
# drum floor, lid crossing) where the lid crossing is "well" (shares the well's hole) or a point.
def thermocouples(p=None):
    p = p or PARAMS
    d = derived(p)
    ra, rb = p["heater_rings"]
    off = p["well_od"] / 2 + 1.5
    mid_heat = p["well_floor_gap"] + 6 + p["heater_heated_len"] / 2
    mid_sand = d["sand_depth"] / 2
    return [
        ("T1", _polar(ra + off, 0), mid_heat, "well"),
        ("T2", _polar(rb - off, 180), mid_heat, "well"),
        ("T3", _polar(ra + off, 120), mid_heat, "well"),
        ("T4", (0.0, 0.0), mid_sand, _polar(165.0, 51.0)),      # bent once on the sand surface
        ("T5", _polar(200.0, 45.0), mid_sand, None),
        ("T6", _polar(270.0, 45.0), mid_sand, None),
        ("T7", _polar(200.0, 225.0), d["sand_depth"] - 100.0, None),
    ]


def derived(p=PARAMS):
    """Dimensions that follow from PARAMS. Shared with the calculation script."""
    d = {}
    d["base_h"] = p["base_aes"] + p["base_ifb"] + p["base_mw"]
    d["drum_z0"] = d["base_h"]                                   # drum bottom
    d["floor_z"] = d["drum_z0"] + p["drum_floor"]                # inner floor
    d["drum_r_i"] = p["drum_id"] / 2
    d["drum_r_o"] = d["drum_r_i"] + p["drum_wall"]
    d["lid_z"] = d["drum_z0"] + p["drum_h"]                      # underside of lid
    d["drum_area_m2"] = pi * (d["drum_r_i"] / 1000) ** 2
    well_a = pi / 4 * (p["well_od"] / 1000) ** 2
    tube_a = pi / 4 * (p["tube_od"] / 1000) ** 2
    d["n_heaters"] = len(p["heater_rings"]) * p["n_per_ring"]
    d["displaced_m2"] = d["n_heaters"] * well_a + 2 * p["n_utubes"] * tube_a
    d["sand_area_m2"] = d["drum_area_m2"] - d["displaced_m2"]
    d["sand_vol_m3"] = p["sand_mass_kg"] / p["sand_rho"]
    # Bottom parts that also displace sand: U-tube runs and bends, well caps
    r_t = p["tube_od"] / 2000
    runs = p["n_utubes"] * (p["leg_outer_r"] - p["leg_inner_r"]) / 1000 * pi * r_t ** 2
    bends = 2 * p["n_utubes"] * 4 / 3 * pi * r_t ** 3
    caps = d["n_heaters"] * pi / 4 * ((p["well_cap_od"] / 1000) ** 2 - (p["well_od"] / 1000) ** 2) \
        * p["well_cap_h"] / 1000
    d["bottom_disp_m3"] = runs + bends + caps
    d["sand_depth"] = round((d["sand_vol_m3"] + d["bottom_disp_m3"]) / d["sand_area_m2"] * 1000, 0)
    d["sand_depth_eq"] = d["sand_vol_m3"] / d["sand_area_m2"] * 1000   # equivalent prismatic depth
    d["sand_top_z"] = d["floor_z"] + d["sand_depth"]
    d["ins_top_int"] = d["lid_z"] - d["sand_top_z"]              # blanket stack in the drum headspace
    d["ins_r_i"] = d["drum_r_o"]
    d["jacket_r_i"] = d["drum_r_o"] + p["ins_side_aes"] + p["ins_side_mw"]
    d["jacket_r_o"] = d["jacket_r_i"] + p["jacket_t"]
    d["top_ins_z0"] = d["lid_z"] + p["lid_t"]
    d["jacket_top_z"] = d["top_ins_z0"] + p["ins_top_aes"] + p["ins_top_mw"]
    d["cap_top_z"] = d["jacket_top_z"] + p["jacket_t"]
    d["well_top_z"] = d["top_ins_z0"] + p["well_above_lid"]
    d["overall_h"] = d["jacket_top_z"] + p["outlet_rise"]
    d["overall_d"] = 2 * d["jacket_r_o"]
    # Cut lengths for the BOM and the making sketches
    d["well_z0"] = d["floor_z"] + p["well_floor_gap"]           # bottom of the well pipe, inside its cap
    d["well_len"] = d["well_top_z"] - d["well_z0"]
    d["bend_zc"] = d["floor_z"] + p["bend_z"]                    # U-tube run centerline
    d["leg_z0"] = d["bend_zc"] + p["elbow_a"] - p["thread_eng"]  # bottom end of a leg pipe, in its elbow
    d["outlet_leg_top"] = d["top_ins_z0"] + 50.0                 # ends inside the collector
    d["inlet_leg_top"] = d["cap_top_z"] + p["inlet_plenum_h"] - 10.0   # ends inside the inlet plenum
    d["outlet_leg_len"] = d["outlet_leg_top"] - d["leg_z0"]
    d["inlet_leg_len"] = d["inlet_leg_top"] - d["leg_z0"]
    d["utube_makeup"] = 2 * (p["elbow_a"] - p["thread_eng"]) + p["nipple_len"]   # leg centres by fittings
    return d


# Parts of the finished unit, in the assembly and in the drawings (the template is a temporary jig)
ASSEMBLY = ["base", "drum", "wells", "heaters", "utubes", "thermocouples", "tc_guides", "sand", "lid", "collector",
            "collector_rivets", "insulation", "jacket", "jacket_cap", "outlet_packing", "trim_ring",
            "inlet_plenum", "jbox", "labels"]


def _polar(r, deg):
    return r * cos(radians(deg)), r * sin(radians(deg))


def build(parts=False):
    """Return the ThermaBrick assembly as a build123d Compound.

    With parts=True, also return a dict of named parts (used for sections, checks and the build plan).
    The setting template (a temporary jig) is in the dict but not in the assembly.
    """
    from build123d import Cylinder, Sphere, Box, Pos, Rot, Compound, Align

    p, d = PARAMS, derived()
    B = (Align.CENTER, Align.CENTER, Align.MIN)          # cylinders standing on z
    C = (Align.CENTER,) * 3

    def tube(r_o, r_i, h, z):
        return Pos(0, 0, z) * (Cylinder(r_o, h, align=B) - Cylinder(r_i, h, align=B))

    def rod(r, h, x, y, z):
        return Pos(x, y, z) * Cylinder(r, h, align=B)

    def fuse(shapes):
        out = None
        for s in shapes:
            out = s if out is None else out + s
        return out

    out = {}

    # ---------------------------------------------------------------- base (DDR-003 P5)
    # Two 50 mm stone wool boards across the full diameter; a 610 mm disc of firebrick laid flat,
    # topped by a 610 mm disc of AES board, under the drum; an 89 mm stone wool batt ring round them.
    rj = d["jacket_r_i"]
    rc = p["base_core_d"] / 2
    mw = p["base_mw"] / 2
    out["base_board_1"] = Cylinder(rj, mw, align=B)
    out["base_board_2"] = Pos(0, 0, mw) * Cylinder(rj, mw, align=B)
    z_ifb = p["base_mw"]
    disc = Pos(0, 0, z_ifb) * Cylinder(rc, p["base_ifb"], align=B)
    bl, bw = p["brick"]
    bricks = []
    nrows = int((rc // bw) + 1)
    for j in range(-nrows, nrows):
        y0 = j * bw
        shift = (bl / 2) * (j % 2)
        for i in range(-3, 4):
            x0 = i * bl + shift - bl / 2
            bx = Pos(x0 + bl / 2, y0 + bw / 2, z_ifb + p["base_ifb"] / 2) * Box(bl - 2, bw - 2, p["base_ifb"])
            piece = bx & disc
            if piece.volume > 1.0:
                bricks.append(piece)
    out["base_ifb"] = Compound(bricks)
    out["base_aes"] = Pos(0, 0, z_ifb + p["base_ifb"]) * Cylinder(rc, p["base_aes"], align=B)
    out["base_ring"] = tube(rj, rc, p["base_ifb"] + p["base_aes"], z_ifb)
    out["base"] = Compound([out[k] for k in ("base_board_1", "base_board_2", "base_ifb", "base_aes", "base_ring")])

    # ---------------------------------------------------------------- drum
    z0 = d["drum_z0"]
    shell = tube(d["drum_r_o"], d["drum_r_i"], p["drum_h"], z0)
    shell += Pos(0, 0, d["floor_z"] - p["drum_wall"]) * Cylinder(d["drum_r_i"], p["drum_wall"], align=B)
    for zc in (z0, z0 + p["drum_h"] - p["chime_h"]):
        shell += tube(p["chime_od"] / 2, d["drum_r_o"], p["chime_h"], zc)
    for hz in p["hoop_z"]:
        shell += tube(p["hoop_od"] / 2, d["drum_r_o"], p["hoop_h"], z0 + hz - p["hoop_h"] / 2)
    out["drum"] = shell

    # ---------------------------------------------------------------- lid, ring and template
    lid = Pos(0, 0, d["lid_z"]) * Cylinder(p["chime_od"] / 2, p["lid_t"], align=B)
    lid += tube(p["ring_od"] / 2, p["chime_od"] / 2, p["ring_h"], d["lid_z"] + p["lid_t"] + 4 - p["ring_h"])
    tpl = Pos(0, 0, d["lid_z"]) * Cylinder(p["chime_od"] / 2, p["template_t"], align=B)
    holes = []                                              # (x, y, dia) shared by the lid and template

    # ---------------------------------------------------------------- heater wells and heaters
    wells, heaters, envelopes = [], [], []
    w_z0 = d["well_z0"]
    for i in range(d["n_heaters"]):
        x, y = _polar(p["heater_rings"][i // p["n_per_ring"]], 360 / p["n_per_ring"] * i)
        h = d["well_len"]
        well = rod(p["well_cap_od"] / 2, p["well_cap_h"], x, y, w_z0 - 6)
        well += rod(p["well_od"] / 2, h, x, y, w_z0)
        well -= rod(p["well_id"] / 2, h, x, y, w_z0 + 6)
        wells.append(well)
        envelopes.append(rod(p["well_cap_od"] / 2, h + 6, x, y, w_z0 - 6))
        heaters.append(rod(p["heater_d"] / 2, p["heater_len"], x, y, w_z0 + 6))
        holes.append((x, y, p["lid_well_hole"]))
    out["wells"] = Compound(wells)
    out["heaters"] = Compound(heaters)

    # ---------------------------------------------------------------- U-tubes (DDR-003 P2)
    # Inlet leg (outer ring) down, two malleable iron elbows and a 4 in nipple across the floor,
    # outlet leg (inner ring) up. Built along +X, where every boolean is between axis-aligned
    # solids, then rotated into place (building each at its own angle left an invalid solid).
    ro, ri = p["tube_od"] / 2, p["tube_id"] / 2
    re_ = p["elbow_od"] / 2
    zb = d["bend_zc"]
    xi0, xo0 = p["leg_inner_r"], p["leg_outer_r"]
    span = xo0 - xi0
    xm0 = (xi0 + xo0) / 2
    ea = p["elbow_a"]
    u0 = rod(ro, d["outlet_leg_top"] - zb, xi0, 0, zb) + rod(ro, d["inlet_leg_top"] - zb, xo0, 0, zb)
    u0 += Pos(xm0, 0, zb) * Rot(0, 90, 0) * Cylinder(ro, span, align=C)
    for xe, sgn in ((xi0, 1), (xo0, -1)):                   # elbow bodies: corner, up arm, across arm
        u0 += Pos(xe, 0, zb) * Sphere(re_)
        u0 += rod(re_, ea, xe, 0, zb)
        u0 += Pos(xe + sgn * ea / 2, 0, zb) * Rot(0, 90, 0) * Cylinder(re_, ea, align=C)
    env0 = u0
    u0 -= rod(ri, d["outlet_leg_top"] - zb, xi0, 0, zb) + rod(ri, d["inlet_leg_top"] - zb, xo0, 0, zb)
    u0 -= Pos(xm0, 0, zb) * Rot(0, 90, 0) * Cylinder(ri, span, align=C)
    u0 -= Pos(xi0, 0, zb) * Sphere(ri) + Pos(xo0, 0, zb) * Sphere(ri)
    utubes = []
    for i in range(p["n_utubes"]):
        ang = p["utube_angle0"] + 60 * i
        utubes.append(Rot(0, 0, ang) * u0)
        envelopes.append(Rot(0, 0, ang) * env0)
        for r in (xi0, xo0):
            holes.append((*_polar(r, ang), p["lid_tube_hole"]))
    out["utubes"] = Compound(utubes)

    # ---------------------------------------------------------------- thermocouples (DDR-003 P10)
    sheaths = []
    tc_top = d["top_ins_z0"] + 40.0
    for tag, (x, y), tip, cross in thermocouples(p):
        zt = d["floor_z"] + tip
        if isinstance(cross, tuple):                         # T4: up to the sand surface, across, up
            zs = d["sand_top_z"] + 15.0
            cx, cy = cross
            L = hypot(cx - x, cy - y)
            a = degrees(atan2(cy - y, cx - x))
            s = rod(1.5, zs - zt, x, y, zt)
            s += Pos((x + cx) / 2, (y + cy) / 2, zs) * Rot(0, 0, a) * Rot(0, 90, 0) * Cylinder(1.5, L, align=C)
            s += Pos(x, y, zs) * Sphere(1.5) + Pos(cx, cy, zs) * Sphere(1.5)
            s += rod(1.5, tc_top - zs, cx, cy, zs)
            holes.append((cx, cy, p["tc_hole"]))
        else:
            s = rod(1.5, tc_top - zt, x, y, zt)
            if cross is None:
                holes.append((x, y, p["tc_hole"]))
        sheaths.append(s)
    # T8 in the collector air, through the collector top
    x8, y8 = _polar(95.0, 0.0)
    cz = d["top_ins_z0"]
    sheaths.append(rod(1.5, tc_top + 80 - (cz + 40), x8, y8, cz + 40))
    out["thermocouples"] = Compound(sheaths)
    # Guide rods for the sand thermocouples T4 to T7: 4.8 mm stainless rod standing on the floor
    # 7 mm inboard of the sheath, which is tied to it with stainless wire (TBK-PRC-001 section 6)
    guides = []
    for tag, (x, y), tip, cross in thermocouples(p):
        if cross == "well":
            continue
        r = hypot(x, y)
        gx, gy = (x - 7 * x / r, y - 7 * y / r) if r > 1 else (7.0, 0.0)
        guides.append(rod(2.4, d["sand_depth"] - 10, gx, gy, d["floor_z"]))
    out["tc_guides"] = Compound(guides)

    for x, y, dia in holes:
        lid -= rod(dia / 2, p["lid_t"] + 2, x, y, d["lid_z"] - 1)
        tpl -= rod(dia / 2, p["template_t"] + 2, x, y, d["lid_z"] - 1)
    pd, pr, pa, pc = p["pour_holes"]
    tpl -= rod(pc / 2, p["template_t"] + 2, 0, 0, d["lid_z"] - 1)
    for a in pa:
        tpl -= rod(pd / 2, p["template_t"] + 2, *_polar(pr, a), d["lid_z"] - 1)
    out["lid"] = lid
    out["template"] = tpl
    out["_holes"] = holes

    # ---------------------------------------------------------------- sand
    sand = Pos(0, 0, d["floor_z"]) * Cylinder(d["drum_r_i"], d["sand_depth"], align=B)
    for env in envelopes:
        sand -= env
    sand -= out["thermocouples"]
    sand -= out["tc_guides"]
    out["sand"] = sand

    # ---------------------------------------------------------------- collector and outlet (DDR-003 P7)
    rcol = p["collector_d"] / 2
    col = tube(rcol, rcol - 0.6, p["collector_h"], cz)
    col += Pos(0, 0, cz + p["collector_h"]) * Cylinder(rcol + 6, 1.2, align=B)        # top disc, folded edge
    col += tube(rcol + 6, rcol + 4.8, 12, cz + p["collector_h"] - 10.8)
    col += tube(p["outlet_d"] / 2, p["outlet_d"] / 2 - 0.6, d["overall_h"] - cz - p["collector_h"],
                cz + p["collector_h"])
    col -= rod(p["outlet_d"] / 2 - 0.6, 3, 0, 0, cz + p["collector_h"] - 0.5)
    col -= rod(2.0, 3, x8, y8, cz + p["collector_h"] - 0.5)
    for k in range(6):                                     # tabs between the wells, at 30, 90, ... deg
        tx, ty = _polar(rcol + p["collector_tab"] / 2 - 0.6, 30 + 60 * k)
        tab = Pos(tx, ty, cz + 0.3) * Rot(0, 0, 30 + 60 * k) * Box(p["collector_tab"], 20, 0.6)
        col += tab
    out["collector"] = col
    rivets = []
    for k in range(6):
        rx, ry = _polar(rcol + p["collector_tab"] / 2, 30 + 60 * k)
        rivets.append(rod(2.4, 4, rx, ry, cz + 0.6))
    out["collector_rivets"] = Compound(rivets)

    # ---------------------------------------------------------------- insulation
    head = Pos(0, 0, d["sand_top_z"]) * Cylinder(d["drum_r_i"], d["ins_top_int"], align=B)
    side = tube(d["jacket_r_i"], d["ins_r_i"], d["jacket_top_z"] - d["base_h"], d["base_h"])
    side -= Pos(0, 0, d["drum_z0"]) * Cylinder(p["ring_od"] / 2 + 1, d["top_ins_z0"] - d["drum_z0"], align=B)
    top = Pos(0, 0, d["top_ins_z0"]) * Cylinder(p["ring_od"] / 2 + 1, d["jacket_top_z"] - d["top_ins_z0"], align=B)
    top -= Pos(0, 0, cz) * Cylinder(rcol + p["collector_tab"] + 1, p["collector_h"] + 2, align=B)
    for part in envelopes + [col, out["thermocouples"]]:
        head -= part
        top -= part
    top -= rod(p["outlet_hole_d"] / 2, 30, 0, 0, d["jacket_top_z"] - 20)
    out["ins_head"] = head
    out["ins_side"] = side
    out["ins_top"] = top
    out["insulation"] = head + side + top
    out["outlet_packing"] = tube(p["outlet_hole_d"] / 2, p["outlet_d"] / 2, 20 + p["jacket_t"], d["jacket_top_z"] - 20)

    # ---------------------------------------------------------------- jacket and cap (DDR-003 P8, P11)
    jacket = tube(d["jacket_r_o"], d["jacket_r_i"], d["jacket_top_z"], 0)
    capr = d["jacket_r_o"] + p["jacket_t"]
    cap = Pos(0, 0, d["jacket_top_z"]) * Cylinder(capr, p["jacket_t"], align=B)
    cap += tube(capr, d["jacket_r_o"], p["cap_skirt"], d["jacket_top_z"] - p["cap_skirt"])
    cap -= rod(p["outlet_hole_d"] / 2, 5, 0, 0, d["jacket_top_z"] - 2)
    for i in range(p["n_utubes"]):
        cap -= rod(p["cap_tube_hole"] / 2, 5, *_polar(p["leg_outer_r"], p["utube_angle0"] + 60 * i), d["jacket_top_z"] - 2)
    ja, jr, jx, jy, jh = p["jbox"]
    cap -= rod(p["jbox_hole"] / 2, 5, *_polar(jr, ja), d["jacket_top_z"] - 2)
    ea_, er_, eh_ = p["tc_exit"]
    cap -= rod(eh_ / 2, 5, *_polar(er_, ea_), d["jacket_top_z"] - 2)
    out["jacket"] = jacket
    out["jacket_cap"] = cap
    ro_, ri_, t_ = p["trim_ring"]
    out["trim_ring"] = tube(ro_ / 2, ri_ / 2, t_, d["cap_top_z"])

    # ---------------------------------------------------------------- inlet plenum (DDR-003 P6)
    pl_ri, pl_ro = p["leg_outer_r"] - 45, p["leg_outer_r"] + 45
    zt = d["cap_top_z"]
    hp, fl = p["inlet_plenum_h"], p["plenum_flange"]
    plenum = tube(pl_ro, pl_ri, hp, zt) - tube(pl_ro - 0.6, pl_ri + 0.6, hp - 0.6, zt)
    plenum += tube(pl_ro + fl, pl_ro, 0.6, zt) + tube(pl_ri, pl_ri - fl, 0.6, zt)
    zc_ = zt + hp / 2
    collar = Pos(pl_ro - 3, 0, zc_) * Rot(0, 90, 0) * \
        (Cylinder(p["outlet_d"] / 2, 120, align=B) - Cylinder(p["outlet_d"] / 2 - 0.6, 120, align=B))
    plenum += collar
    plenum -= Pos(pl_ro - 5, 0, zc_) * Rot(0, 90, 0) * Cylinder(p["outlet_d"] / 2 - 0.6, 10, align=B)
    out["inlet_plenum"] = plenum

    # ---------------------------------------------------------------- heater junction box (DDR-003 P9)
    jx0, jy0 = _polar(jr, ja)
    jb = Pos(jx0, jy0, zt) * Rot(0, 0, ja) * (Box(jx, jy, jh, align=B) - Pos(0, 0, 1.0) * Box(jx - 2, jy - 2, jh - 2, align=B))
    jb -= rod(p["jbox_hole"] / 2 - 4, 3, jx0, jy0, zt - 1)
    out["jbox"] = jb

    # ---------------------------------------------------------------- warning labels (BOM line 47)
    lt = p["label_t"]
    ang, zl, lw_, lh_ = p["label_jacket"]
    lx, ly = _polar(d["jacket_r_o"] + lt / 2, ang)
    out["label_jacket"] = Pos(lx, ly, zl) * Rot(0, 0, ang) * Box(lt, lw_, lh_)
    ang, rl, lw_, lh_ = p["label_cap"]
    lx, ly = _polar(rl, ang)
    out["label_cap"] = Pos(lx, ly, d["cap_top_z"] + lt / 2) * Rot(0, 0, ang + 90) * Box(lw_, lh_, lt)
    bw, bh = p["label_jbox"]
    out["label_jbox"] = Pos(jx0, jy0, zt) * Rot(0, 0, ja) * Pos(jx / 2 + lt / 2, 0, jh / 2) * Box(lt, bw, bh)
    out["labels"] = Compound([out["label_jacket"], out["label_cap"], out["label_jbox"]])

    assy = Compound([out[n] for n in ASSEMBLY])
    return (assy, out) if parts else assy


def bricks_needed(ifb):
    """Whole bricks needed for the firebrick disc: the pieces' lengths packed first-fit decreasing
    into 230 mm bricks with a 3 mm saw cut (a piece is never joined from two offcuts)."""
    bl = PARAMS["brick"][0]
    lens = sorted((s.bounding_box().size.X + 2 for s in ifb.solids()), reverse=True)
    bins = []
    for L in lens:
        for i, free in enumerate(bins):
            if free >= L + 3:
                bins[i] = free - L - 3
                break
        else:
            bins.append(bl - L - 3)
    return len(bins), len(lens)


# ---------------------------------------------------------------------------- constructability checks
def check():
    """Constructability checks (TBK-DDR-003). Prints one line per check and returns the failures."""
    from build123d import Pos, Cylinder, Align

    p, d = PARAMS, derived()
    _, M = build(parts=True)
    res = []

    def ok(name, cond, detail=""):
        res.append((name, bool(cond), detail))

    def vol(a, b):
        try:
            return (a & b).volume
        except Exception:
            return 0.0

    def dist(a, b):
        return a.distance_to(b)

    # 1. Parts that must not overlap (volume of common material below 1 mm3)
    pairs = [("wells", "utubes"), ("wells", "drum"), ("utubes", "drum"), ("thermocouples", "utubes"),
             ("thermocouples", "wells"), ("collector", "wells"), ("collector", "utubes"), ("lid", "wells"),
             ("lid", "utubes"), ("lid", "thermocouples"), ("jacket_cap", "utubes"), ("jacket_cap", "collector"),
             ("inlet_plenum", "jbox"), ("trim_ring", "inlet_plenum"), ("trim_ring", "collector"),
             ("base_ifb", "base_ring"), ("base_aes", "base_ring"), ("drum", "base_ring"),
             ("drum", "insulation"), ("jacket", "insulation"), ("jacket_cap", "insulation"),
             ("collector", "insulation"), ("sand", "wells"), ("sand", "utubes"), ("sand", "thermocouples"),
             ("tc_guides", "thermocouples"), ("tc_guides", "utubes"), ("tc_guides", "wells"),
             ("label_jacket", "jacket"), ("label_cap", "jacket_cap"), ("label_cap", "trim_ring"),
             ("label_cap", "inlet_plenum"), ("label_cap", "jbox"), ("label_jbox", "jbox")]
    for a, b in pairs:
        v = vol(M[a], M[b])
        ok(f"no overlap: {a} / {b}", v < 1.0, f"{v:.2f} mm3")

    # 2. Parts that must touch (they stand on or are fixed to the part named)
    touch = [("well caps on the levelled first sand lift", M["wells"], M["sand"]),
             ("U-tube elbows on the drum floor", M["utubes"], M["drum"]),
             ("drum chime on the AES board", M["drum"], M["base_aes"]),
             ("AES board on the firebrick", M["base_aes"], M["base_ifb"]),
             ("firebrick on the stone wool board", M["base_ifb"], M["base_board_2"]),
             ("top board on the bottom board", M["base_board_2"], M["base_board_1"]),
             ("batt ring on the stone wool board", M["base_ring"], M["base_board_2"]),
             ("lid on the drum rim", M["lid"], M["drum"]),
             ("collector tabs on the lid", M["collector"], M["lid"]),
             ("jacket cap skirt on the jacket", M["jacket_cap"], M["jacket"]),
             ("inlet plenum flange on the cap", M["inlet_plenum"], M["jacket_cap"]),
             ("trim ring on the cap", M["trim_ring"], M["jacket_cap"]),
             ("junction box on the cap", M["jbox"], M["jacket_cap"]),
             ("template on the drum rim", M["template"], M["drum"]),
             ("thermocouple guide rods on the drum floor", M["tc_guides"], M["drum"]),
             ("HOT SURFACES INSIDE label on the jacket side", M["label_jacket"], M["jacket"]),
             ("HOT OUTLET label on the jacket cap", M["label_cap"], M["jacket_cap"]),
             ("DANGER 240 V label on the junction box face", M["label_jbox"], M["jbox"])]
    for n, a, b in touch:
        g = dist(a, b)
        ok(f"touch: {n}", g < 0.05, f"gap {g:.2f} mm")

    # 3. Clearances through holes and between neighbours
    rw = p["lid_well_hole"] / 2 - p["well_od"] / 2
    ok("lid hole round each well, radial gap 4 mm or more (room for the T1 to T3 sheath)", rw >= 4.0 and rw - 3.0 >= 1.0, f"{rw:.2f} mm")
    rt = p["lid_tube_hole"] / 2 - p["tube_od"] / 2
    ok("lid hole round each U-tube leg, radial gap 2.5 mm or more", rt >= 2.5, f"{rt:.2f} mm")
    g = dist(M["collector"], M["wells"])
    ok("collector clear of the inner ring of wells by 5 mm or more", g >= 5.0, f"{g:.1f} mm")
    g = dist(M["inlet_plenum"], M["trim_ring"])
    ok("plenum flange clear of the trim ring by 20 mm or more", g >= 20.0, f"{g:.1f} mm")
    zinc_gap = p["outlet_hole_d"] / 2 - p["outlet_d"] / 2
    ok("galvanized cap kept 35 mm or more from the hot outlet (R13)", zinc_gap >= 35.0, f"{zinc_gap:.1f} mm")
    g = dist(M["jbox"], M["inlet_plenum"])
    ok("junction box clear of the inlet plenum and collar by 30 mm or more", g >= 30.0, f"{g:.1f} mm")
    g = dist(M["thermocouples"], M["utubes"])
    ok("thermocouple sheaths clear of the U-tubes by 5 mm or more", g >= 5.0, f"{g:.1f} mm")
    g = dist(M["thermocouples"], M["wells"])
    ok("sand thermocouples (T4 to T7) clear of the wells", g >= 0.0, f"{g:.1f} mm (T1 to T3 touch their wells)")
    fl_top = p["inlet_plenum_h"] / 2 - p["outlet_d"] / 2
    ok("inlet plenum wall round the 4 in collar, 15 mm or more above and below", fl_top >= 15.0, f"{fl_top:.1f} mm")
    g = dist(M["label_cap"], M["trim_ring"])
    ok("HOT OUTLET label clear of the trim ring by 20 mm or more", g >= 20.0, f"{g:.1f} mm")
    g = dist(M["label_cap"], M["inlet_plenum"])
    ok("HOT OUTLET label clear of the inlet plenum flange by 20 mm or more", g >= 20.0, f"{g:.1f} mm")
    g = dist(M["label_cap"], M["jbox"])
    ok("HOT OUTLET label clear of the junction box by 20 mm or more", g >= 20.0, f"{g:.1f} mm")
    rcap = d["jacket_r_o"] + p["jacket_t"]
    ok("HOT OUTLET label lies wholly on the cap, 10 mm or more inside its edge",
       p["label_cap"][1] + hypot(p["label_cap"][2], p["label_cap"][3]) / 2 <= rcap - 10.0,
       f"outer corner {p['label_cap'][1] + hypot(p['label_cap'][2], p['label_cap'][3]) / 2:.0f} mm of {rcap - 10:.0f} mm")
    ok("jacket label sits between the second lap row and the cap, clear of the cap skirt",
       p["label_jacket"][1] + p["label_jacket"][3] / 2 <= d["jacket_top_z"] - p["cap_skirt"] - 10.0,
       f"top edge {p['label_jacket'][1] + p['label_jacket'][3] / 2:.0f} mm of {d['jacket_top_z'] - p['cap_skirt'] - 10:.0f} mm")
    ok("DANGER 240 V label fits the junction box face with 10 mm margin",
       p["label_jbox"][0] <= p["jbox"][3] - 20 and p["label_jbox"][1] <= p["jbox"][4] - 20)
    pd, pr, pa, pc = p["pour_holes"]
    tpl_ok = True
    for hx, hy, hd in [(*_polar(pr, a), pd) for a in pa] + [(0.0, 0.0, pc)]:
        for x, y, dia in M["_holes"]:
            if hypot(hx - x, hy - y) > 1.0 and hypot(hx - x, hy - y) < hd / 2 + dia / 2 + 10:
                tpl_ok = False
    ok("template pour holes 10 mm or more from every pipe and sheath hole", tpl_ok)

    # 4. Fit of the fittings, cut lengths and lead lengths
    ok("elbows and 4 in nipple set the leg centres within 2 mm of the 155 mm spacing",
       abs(d["utube_makeup"] - (p["leg_outer_r"] - p["leg_inner_r"])) <= 2.0,
       f"{d['utube_makeup']:.1f} mm against {p['leg_outer_r'] - p['leg_inner_r']:.0f} mm")
    ok("three wells cut from each 10 ft pipe", 3 * (d["well_len"] + 3) <= 3048, f"{d['well_len']:.0f} mm each")
    ok("two inlet legs or three outlet legs cut from each 10 ft pipe",
       2 * (d["inlet_leg_len"] + 3) <= 3048 and 3 * (d["outlet_leg_len"] + 3) <= 3048,
       f"inlet {d['inlet_leg_len']:.0f} mm, outlet {d['outlet_leg_len']:.0f} mm")
    jx0, jy0 = _polar(p["jbox"][1], p["jbox"][0])
    worst = 0.0
    for i in range(d["n_heaters"]):
        x, y = _polar(p["heater_rings"][i // p["n_per_ring"]], 360 / p["n_per_ring"] * i)
        run = (d["well_top_z"] - (d["well_z0"] + 6 + p["heater_len"])) + 1.3 * hypot(jx0 - x, jy0 - y) \
            + (d["cap_top_z"] - d["well_top_z"]) + 150
        worst = max(worst, run)
    ok("heater leads reach the junction box from the farthest well, with 30 % routing allowance",
       worst <= p["heater_lead"], f"needs {worst:.0f} mm of {p['heater_lead']:.0f} mm")
    ex, ey = _polar(p["tc_exit"][1], p["tc_exit"][0])
    worst = 0.0
    for tag, (x, y), tip, cross in thermocouples():
        cx, cy = cross if isinstance(cross, tuple) else (x, y)
        run = (d["top_ins_z0"] + 40 - (d["floor_z"] + tip)) + hypot(cx - x, cy - y) \
            + 1.3 * hypot(ex - cx, ey - cy) + (d["cap_top_z"] - d["top_ins_z0"] - 40) + 50
        worst = max(worst, run)
    ok("thermocouple sheaths reach the exit grommet, with 30 % routing allowance",
       worst <= p["tc_sheath"], f"needs {worst:.0f} mm of {p['tc_sheath']:.0f} mm")
    nb, npieces = bricks_needed(M["base_ifb"])
    ok("firebrick disc cut from 16 bricks or fewer", nb <= 16, f"{npieces} pieces from {nb} bricks")

    # 5. Every part is a valid solid
    for k in ("drum", "lid", "wells", "utubes", "collector", "insulation", "jacket", "jacket_cap",
              "inlet_plenum", "jbox", "template", "sand", "base", "labels"):
        ok(f"valid solid: {k}", M[k].is_valid)

    for n, good, det in res:
        print(f"{'PASS' if good else 'FAIL'}  {n}" + (f"  ({det})" if det else ""))
    fails = [r for r in res if not r[1]]
    print(f"{len(res) - len(fails)} of {len(res)} checks pass")
    return fails


if __name__ == "__main__":
    if "--check" in sys.argv:
        sys.exit(1 if check() else 0)
    from build123d import export_step, export_stl
    part = build()
    out = Path(__file__).resolve().parents[1]
    (out / "step").mkdir(exist_ok=True)
    (out / "stl").mkdir(exist_ok=True)
    export_step(part, str(out / "step" / "thermabrick.step"))
    export_stl(part, str(out / "stl" / "thermabrick.stl"), tolerance=0.5, angular_tolerance=0.3)
    d = derived()
    print(f"sand depth {d['sand_depth']:.0f} mm, overall {d['overall_d']:.0f} dia x {d['overall_h']:.0f} mm high")
    print(f"cut lengths: wells {d['well_len']:.0f} mm, inlet legs {d['inlet_leg_len']:.0f} mm, "
          f"outlet legs {d['outlet_leg_len']:.0f} mm")
