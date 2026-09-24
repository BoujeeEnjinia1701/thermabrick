"""ThermaBrick parametric model (build123d).

Run from the repo root:  python cad/src/model.py
Exports STEP and STL into cad/step and cad/stl.

PARAMS is the single source of truth for geometry. The sizing script
docs/04-calcs/tbk_cal_001.py imports it, so every number in TBK-CAL-001 comes
from the same dimensions that the CAD model and TBK-DWG-001 show.

Coordinate frame: origin at floor level on the drum axis, +Z up, millimeters.
"""
from math import cos, sin, radians, pi
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
    "well_floor_gap": 20.0,      # well cap clearance above drum floor
    "well_cap_od": 33.0,
    "well_cap_h": 25.0,
    "heater_d": 15.9,            # 5/8 in cartridge heater
    "heater_len": 508.0,         # 20 in overall
    "heater_w": 250.0,           # W at 240 V
    "heater_heated_len": 457.0,  # 18 in heated, 2 in cold end at the lead end

    # Discharge heat exchanger: six U-tubes of 1-1/4 in Sch 40 black steel pipe
    "n_utubes": 6,
    "leg_inner_r": 80.0,         # outlet (hot) legs, into the collector
    "leg_outer_r": 235.0,        # inlet (cold) legs, from the inlet plenum
    "utube_angle0": 30.0,        # deg; U-tubes at 30, 90, 150 ... (between the heater wells)
    "tube_od": 42.2,
    "tube_id": 35.1,
    "bend_z": 50.0,              # U-bend centerline above drum floor

    # Hot collector and outlet on the lid
    "collector_d": 254.0,        # 10 in black steel stovepipe section
    "collector_h": 80.0,
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
    "jacket_t": 0.6,             # 26 ga galvanized steel wrapper

    # Heater wells stop just above the lid; the ceramic-beaded leads run up through the top
    # insulation to a junction box on the jacket top, so no well crosses the top insulation.
    "well_above_lid": 25.0,
    "inlet_plenum_h": 110.0,     # annular inlet plenum on the jacket top
}


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
    d["well_top_z"] = d["top_ins_z0"] + p["well_above_lid"]
    d["overall_h"] = d["jacket_top_z"] + p["outlet_rise"]
    d["overall_d"] = 2 * d["jacket_r_o"]
    return d


def _polar(r, deg):
    return r * cos(radians(deg)), r * sin(radians(deg))


def build(parts=False):
    """Return the ThermaBrick assembly as a build123d Compound.

    With parts=True, also return a dict of named parts (used for sections and checks).
    """
    from build123d import Cylinder, Sphere, Pos, Rot, Compound, Align

    p, d = PARAMS, derived()
    B = (Align.CENTER, Align.CENTER, Align.MIN)          # cylinders standing on z
    C = (Align.CENTER,) * 3

    def tube(r_o, r_i, h, z):
        return Pos(0, 0, z) * (Cylinder(r_o, h, align=B) - Cylinder(r_i, h, align=B))

    def rod(r, h, x, y, z):
        return Pos(x, y, z) * Cylinder(r, h, align=B)

    out = {}

    # Base: AES board, insulating firebrick and stone wool board, shown as one body
    out["base"] = Cylinder(d["jacket_r_i"], d["base_h"], align=B)

    # Drum body, floor, chimes and rolling hoops
    z0 = d["drum_z0"]
    shell = tube(d["drum_r_o"], d["drum_r_i"], p["drum_h"], z0)
    shell += Pos(0, 0, d["floor_z"] - p["drum_wall"]) * Cylinder(d["drum_r_i"], p["drum_wall"], align=B)
    for zc in (z0, z0 + p["drum_h"] - p["chime_h"]):
        shell += tube(p["chime_od"] / 2, d["drum_r_o"], p["chime_h"], zc)
    for hz in p["hoop_z"]:
        shell += tube(p["hoop_od"] / 2, d["drum_r_o"], p["hoop_h"], z0 + hz - p["hoop_h"] / 2)
    out["drum"] = shell

    # Lid and closing ring
    lid = Pos(0, 0, d["lid_z"]) * Cylinder(p["chime_od"] / 2, p["lid_t"], align=B)
    lid += tube(p["ring_od"] / 2, p["chime_od"] / 2, p["ring_h"], d["lid_z"] + p["lid_t"] + 4 - p["ring_h"])

    # Heater wells with bottom caps, and cartridge heaters
    wells, heaters, envelopes = [], [], []
    w_z0 = d["floor_z"] + p["well_floor_gap"]
    for i in range(d["n_heaters"]):
        x, y = _polar(p["heater_rings"][i // p["n_per_ring"]], 360 / p["n_per_ring"] * i)
        h = d["well_top_z"] - w_z0
        well = rod(p["well_cap_od"] / 2, p["well_cap_h"], x, y, w_z0 - 6)
        well += rod(p["well_od"] / 2, h, x, y, w_z0)
        well -= rod(p["well_id"] / 2, h, x, y, w_z0 + 6)
        wells.append(well)
        envelopes.append(rod(p["well_cap_od"] / 2, h + 6, x, y, w_z0 - 6))
        heaters.append(rod(p["heater_d"] / 2, p["heater_len"], x, y, w_z0 + 6))
        lid -= rod(p["well_od"] / 2 + 1, p["lid_t"] + 2, x, y, d["lid_z"] - 1)
    out["wells"] = Compound(wells)
    out["heaters"] = Compound(heaters)

    # U-tubes: inlet leg (outer ring) down, radial run across the bottom, outlet leg (inner ring) up
    utubes = []
    ro, ri = p["tube_od"] / 2, p["tube_id"] / 2
    zb = d["floor_z"] + p["bend_z"]
    top_in = d["lid_z"] + p["lid_t"] + 50                       # outlet legs end inside the collector
    top_out = d["jacket_top_z"] + p["inlet_plenum_h"] - 10      # inlet legs end inside the inlet plenum
    for i in range(p["n_utubes"]):
        ang = p["utube_angle0"] + 60 * i
        xi, yi = _polar(p["leg_inner_r"], ang)
        xo, yo = _polar(p["leg_outer_r"], ang)
        span = p["leg_outer_r"] - p["leg_inner_r"]
        xm, ym = _polar((p["leg_outer_r"] + p["leg_inner_r"]) / 2, ang)
        u = rod(ro, top_in - zb, xi, yi, zb) + rod(ro, top_out - zb, xo, yo, zb)
        u += Pos(xm, ym, zb) * Rot(0, 0, ang) * Rot(0, 90, 0) * Cylinder(ro, span, align=C)
        u += Pos(xi, yi, zb) * Sphere(ro) + Pos(xo, yo, zb) * Sphere(ro)
        u -= rod(ri, top_in - zb, xi, yi, zb) + rod(ri, top_out - zb, xo, yo, zb)
        u -= Pos(xm, ym, zb) * Rot(0, 0, ang) * Rot(0, 90, 0) * Cylinder(ri, span, align=C)
        u -= Pos(xi, yi, zb) * Sphere(ri) + Pos(xo, yo, zb) * Sphere(ri)
        utubes.append(u)
        env = rod(ro, top_in - zb, xi, yi, zb) + rod(ro, top_out - zb, xo, yo, zb)
        env += Pos(xm, ym, zb) * Rot(0, 0, ang) * Rot(0, 90, 0) * Cylinder(ro, span, align=C)
        envelopes.append(env + Pos(xi, yi, zb) * Sphere(ro) + Pos(xo, yo, zb) * Sphere(ro))
        for (x, y) in ((xi, yi), (xo, yo)):
            lid -= rod(ro + 1, p["lid_t"] + 2, x, y, d["lid_z"] - 1)
    out["utubes"] = Compound(utubes)
    out["lid"] = lid

    # Sand fill, displaced by wells and tubes
    sand = Pos(0, 0, d["floor_z"]) * Cylinder(d["drum_r_i"], d["sand_depth"], align=B)
    for env in envelopes:
        sand -= env
    out["sand"] = sand

    # Hot collector with 4 in outlet
    cz = d["lid_z"] + p["lid_t"]
    col = tube(p["collector_d"] / 2, p["collector_d"] / 2 - 0.6, p["collector_h"], cz)
    col += Pos(0, 0, cz + p["collector_h"]) * Cylinder(p["collector_d"] / 2, 0.8, align=B)
    col += tube(p["outlet_d"] / 2, p["outlet_d"] / 2 - 0.6, d["overall_h"] - cz - p["collector_h"],
                cz + p["collector_h"])
    col -= rod(p["outlet_d"] / 2 - 0.6, 2, 0, 0, cz + p["collector_h"] - 0.5)
    out["collector"] = col

    # Insulation: blanket stack in the drum headspace, side wrap, top blanket and batts
    ins = Pos(0, 0, d["sand_top_z"]) * Cylinder(d["drum_r_i"], d["ins_top_int"], align=B)
    ins += tube(d["jacket_r_i"], d["ins_r_i"], d["jacket_top_z"] - d["base_h"], d["base_h"])
    ins += Pos(0, 0, d["top_ins_z0"]) * Cylinder(d["ins_r_i"], d["jacket_top_z"] - d["top_ins_z0"], align=B)
    ins -= Pos(0, 0, d["drum_z0"]) * Cylinder(p["ring_od"] / 2 + 1, d["top_ins_z0"] - d["drum_z0"], align=B) \
        - Pos(0, 0, d["drum_z0"]) * Cylinder(d["drum_r_i"], d["lid_z"] - d["drum_z0"], align=B)
    ins -= Pos(0, 0, cz) * Cylinder(p["collector_d"] / 2, p["collector_h"] + 1, align=B)
    for part in envelopes + [col]:
        ins -= part
    out["insulation"] = ins

    # Jacket and annular inlet plenum with 4 in inlet collar
    jacket = tube(d["jacket_r_o"], d["jacket_r_i"], d["jacket_top_z"], 0)
    jacket += Pos(0, 0, d["jacket_top_z"]) * Cylinder(d["jacket_r_o"], p["jacket_t"], align=B)
    pl_ri, pl_ro = p["leg_outer_r"] - 45, p["leg_outer_r"] + 45
    zt = d["jacket_top_z"] + p["jacket_t"]
    plenum = tube(pl_ro, pl_ri, p["inlet_plenum_h"], zt) - tube(pl_ro - 0.8, pl_ri + 0.8, p["inlet_plenum_h"] - 0.8, zt)
    collar = Pos(pl_ro - 5, 0, zt + p["inlet_plenum_h"] / 2) * Rot(0, 90, 0) * \
        (Cylinder(p["outlet_d"] / 2, 120, align=B) - Cylinder(p["outlet_d"] / 2 - 0.6, 120, align=B))
    plenum += collar
    for part in utubes + [col]:
        jacket -= part
    out["jacket"] = jacket
    out["inlet_plenum"] = plenum

    names = ["base", "drum", "lid", "wells", "heaters", "utubes", "sand", "insulation",
             "collector", "jacket", "inlet_plenum"]
    assy = Compound([out[n] for n in names])
    return (assy, out) if parts else assy


if __name__ == "__main__":
    from build123d import export_step, export_stl
    part = build()
    out = Path(__file__).resolve().parents[1]
    export_step(part, str(out / "step" / "thermabrick.step"))
    export_stl(part, str(out / "stl" / "thermabrick.stl"))
    d = derived()
    print(f"sand depth {d['sand_depth']:.0f} mm, overall {d['overall_d']:.0f} dia x {d['overall_h']:.0f} mm high")
