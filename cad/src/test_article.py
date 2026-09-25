"""ThermaBrick reduced-scale test article (build123d).

Run from the repo root:  python cad/src/test_article.py
Exports STEP and STL into cad/step and cad/stl as thermabrick-test-article.*

A 16 US gal drum with 68 kg of sand (about 6 kWh(th)) and four heater cells that match
the full-scale design (same heater, well and cell spacing), one U-tube and a 120 V supply.
PARAMS is the single source of truth; docs/04-calcs/tbk_cal_002.py imports it.

Coordinate frame: origin at floor level on the drum axis, +Z up, millimeters.
"""
from math import pi
from pathlib import Path

PARAMS = {
    # Vessel: 16 US gal open-head steel drum, unlined, 20 ga (Uline S-19411)
    "drum_id": 342.9,            # 13.5 in
    "drum_wall": 0.9,            # 20 ga
    "drum_h": 673.0,             # 26.5 in overall
    "drum_floor": 12.0,          # inner floor above drum bottom
    "chime_od": 368.0,
    "chime_h": 8.0,
    "hoop_od": 356.0,
    "hoop_h": 12.0,
    "hoop_z": (224.0, 449.0),
    "lid_t": 0.9,
    "ring_od": 378.0,            # 14-7/8 in over the closing ring
    "ring_h": 18.0,

    # Storage medium: three 50 lb bags of washed play sand
    "sand_mass_kg": 68.0,
    "sand_rho": 1600.0,

    # Four heater cells, same heater and well as the full-scale design
    "heater_xy": ((90.0, 75.0), (-90.0, 75.0), (-90.0, -75.0), (90.0, -75.0)),
    "well_od": 26.7,             # 3/4 in Sch 40 black steel, bottom crimped closed
    "well_id": 20.9,
    "well_floor_gap": 20.0,
    "well_crimp_h": 10.0,
    "well_above_lid": 25.0,
    "heater_d": 15.9,            # 5/8 in cartridge heater
    "heater_len": 457.0,         # 18 in overall
    "heater_heated_len": 406.0,  # 16 in heated, 2 in cold end at the lead end
    "heater_w": 250.0,           # W at 120 V

    # One U-tube of 1-1/4 in Sch 40 black steel pipe along the Y axis
    "n_utubes": 1,
    "tube_od": 42.2,
    "tube_id": 35.1,
    "leg_span": 206.4,           # leg centers: two elbows on a 1-1/4 x 6 in nipple
    "bend_z": 50.0,
    "leg_nipple": 914.4,         # 1-1/4 x 36 in nipple; the shortest stock length that reaches
    "elbow_offset": 27.2,        # elbow center to nipple end: 44.5 center-to-end less 17.3 engagement

    # Dilution stack over the outlet leg: 4 in black stovepipe, open at both ends
    "stack_d": 101.6,
    "stack_len": 610.0,
    "stack_overlap": 40.0,       # outlet leg ends this far inside the stack's open bottom

    # Insulation: stone wool throughout, bricks on edge under the chime
    "ins_side": 267.0,           # 3 x 89 mm stone wool batt
    "ins_top": 178.0,            # 2 x 89 mm above the lid
    "base_h": 114.0,             # K-23 bricks on edge, stone wool between
    "brick": (230.0, 64.0, 114.0),
    "n_bricks": 4,
    "brick_r": 150.0,            # brick centers, radial, so each spans r 35 to 265 under the chime
    "jacket_t": 0.5,             # aluminum roll flashing, 20 in x 25 ft

    # Inlet blower (12 V centrifugal, 97 x 94 x 33 mm) on the inlet leg
    "blower": (97.0, 94.0, 33.0),
}


def derived(p=PARAMS):
    d = {}
    d["n_heaters"] = len(p["heater_xy"])
    d["drum_z0"] = p["base_h"]
    d["floor_z"] = d["drum_z0"] + p["drum_floor"]
    d["drum_r_i"] = p["drum_id"] / 2
    d["drum_r_o"] = d["drum_r_i"] + p["drum_wall"]
    d["lid_z"] = d["drum_z0"] + p["drum_h"]
    d["drum_area_m2"] = pi * (d["drum_r_i"] / 1000) ** 2
    well_a = pi / 4 * (p["well_od"] / 1000) ** 2
    r_t = p["tube_od"] / 2000
    d["displaced_m2"] = d["n_heaters"] * well_a + 2 * p["n_utubes"] * pi * r_t ** 2
    d["sand_area_m2"] = d["drum_area_m2"] - d["displaced_m2"]
    d["sand_vol_m3"] = p["sand_mass_kg"] / p["sand_rho"]
    d["bottom_disp_m3"] = p["n_utubes"] * (p["leg_span"] / 1000 * pi * r_t ** 2 + 2 * 4 / 3 * pi * r_t ** 3)
    d["sand_depth_eq"] = d["sand_vol_m3"] / d["sand_area_m2"] * 1000
    d["sand_depth"] = round((d["sand_vol_m3"] + d["bottom_disp_m3"]) / d["sand_area_m2"] * 1000, 0)
    d["sand_top_z"] = d["floor_z"] + d["sand_depth"]
    d["ins_top_int"] = d["lid_z"] - d["sand_top_z"]
    d["jacket_r_i"] = d["drum_r_o"] + p["ins_side"]
    d["jacket_r_o"] = d["jacket_r_i"] + p["jacket_t"]
    d["top_ins_z0"] = d["lid_z"] + p["lid_t"]
    d["jacket_top_z"] = d["top_ins_z0"] + p["ins_top"]
    d["well_top_z"] = d["top_ins_z0"] + p["well_above_lid"]
    d["leg_top_z"] = d["floor_z"] + p["bend_z"] + p["elbow_offset"] + p["leg_nipple"]
    d["leg_above_jacket"] = d["leg_top_z"] - d["jacket_top_z"]
    d["stack_z0"] = d["leg_top_z"] - p["stack_overlap"]
    d["well_cut"] = d["well_top_z"] - (d["floor_z"] + p["well_floor_gap"]) + 25.0   # 25 mm crimp allowance
    d["overall_h"] = d["stack_z0"] + p["stack_len"]
    d["overall_d"] = 2 * d["jacket_r_o"]
    return d


def build(parts=False):
    from build123d import Cylinder, Sphere, Box, Pos, Rot, Compound, Align

    p, d = PARAMS, derived()
    B = (Align.CENTER, Align.CENTER, Align.MIN)
    C = (Align.CENTER,) * 3

    def tube(r_o, r_i, h, z, x=0.0, y=0.0):
        return Pos(x, y, z) * (Cylinder(r_o, h, align=B) - Cylinder(r_i, h, align=B))

    def rod(r, h, x, y, z):
        return Pos(x, y, z) * Cylinder(r, h, align=B)

    out = {}

    # Base: four insulating firebricks on edge under the chime, stone wool batt between
    bl, bw, bh = p["brick"]
    bricks = []
    for i in range(p["n_bricks"]):
        ang = 45 + 360 / p["n_bricks"] * i
        bricks.append(Rot(0, 0, ang) * Pos(p["brick_r"], 0, 0) * Box(bl, bw, bh, align=B))
    out["bricks"] = Compound(bricks)
    base = Cylinder(d["jacket_r_i"], p["base_h"], align=B)
    for b in bricks:
        base -= b
    out["base_wool"] = base

    # Drum
    z0 = d["drum_z0"]
    shell = tube(d["drum_r_o"], d["drum_r_i"], p["drum_h"], z0)
    shell += Pos(0, 0, d["floor_z"] - p["drum_wall"]) * Cylinder(d["drum_r_i"], p["drum_wall"], align=B)
    for zc in (z0, z0 + p["drum_h"] - p["chime_h"]):
        shell += tube(p["chime_od"] / 2, d["drum_r_o"], p["chime_h"], zc)
    for hz in p["hoop_z"]:
        shell += tube(p["hoop_od"] / 2, d["drum_r_o"], p["hoop_h"], z0 + hz - p["hoop_h"] / 2)
    out["drum"] = shell
    lid = Pos(0, 0, d["lid_z"]) * Cylinder(p["chime_od"] / 2, p["lid_t"], align=B)
    lid += tube(p["ring_od"] / 2, p["chime_od"] / 2, p["ring_h"], d["lid_z"] + p["lid_t"] + 3 - p["ring_h"])

    # Heater wells and heaters
    wells, heaters, envelopes = [], [], []
    w_z0 = d["floor_z"] + p["well_floor_gap"]
    h = d["well_top_z"] - w_z0
    for x, y in p["heater_xy"]:
        well = rod(p["well_od"] / 2, h, x, y, w_z0) - rod(p["well_id"] / 2, h, x, y, w_z0 + p["well_crimp_h"])
        wells.append(well)
        envelopes.append(rod(p["well_od"] / 2, h, x, y, w_z0))
        heaters.append(rod(p["heater_d"] / 2, p["heater_len"], x, y, w_z0 + p["well_crimp_h"]))
        lid -= rod(p["well_od"] / 2 + 1, p["lid_t"] + 2, x, y, d["lid_z"] - 1)
    out["wells"] = Compound(wells)
    out["heaters"] = Compound(heaters)

    # U-tube along Y: inlet leg at -Y, outlet leg at +Y
    ro, ri = p["tube_od"] / 2, p["tube_id"] / 2
    zb = d["floor_z"] + p["bend_z"]
    a = p["leg_span"] / 2
    L = d["leg_top_z"] - zb
    u = rod(ro, L, 0, -a, zb) + rod(ro, L, 0, a, zb)
    u += Pos(0, 0, zb) * Rot(90, 0, 0) * Cylinder(ro, 2 * a, align=C)
    u += Pos(0, -a, zb) * Sphere(ro) + Pos(0, a, zb) * Sphere(ro)
    env = u
    u -= rod(ri, L, 0, -a, zb) + rod(ri, L, 0, a, zb)
    u -= Pos(0, 0, zb) * Rot(90, 0, 0) * Cylinder(ri, 2 * a, align=C)
    u -= Pos(0, -a, zb) * Sphere(ri) + Pos(0, a, zb) * Sphere(ri)
    out["utube"] = u
    envelopes.append(env)
    for y in (-a, a):
        lid -= rod(ro + 1, p["lid_t"] + 2, 0, y, d["lid_z"] - 1)
    out["lid"] = lid

    # Sand
    sand = Pos(0, 0, d["floor_z"]) * Cylinder(d["drum_r_i"], d["sand_depth"], align=B)
    for e in envelopes:
        sand -= e
    out["sand"] = sand

    # Insulation: headspace, side wrap, top
    ins = Pos(0, 0, d["sand_top_z"]) * Cylinder(d["drum_r_i"], d["ins_top_int"], align=B)
    ins += tube(d["jacket_r_i"], d["drum_r_o"], d["jacket_top_z"] - p["base_h"], p["base_h"])
    ins += Pos(0, 0, d["top_ins_z0"]) * Cylinder(d["drum_r_o"], d["jacket_top_z"] - d["top_ins_z0"], align=B)
    ins -= Pos(0, 0, z0) * Cylinder(p["ring_od"] / 2 + 1, d["top_ins_z0"] - z0, align=B) \
        - Pos(0, 0, z0) * Cylinder(d["drum_r_i"], d["lid_z"] - z0, align=B)
    for e in envelopes:
        ins -= e
    out["insulation"] = ins

    # Jacket
    jacket = tube(d["jacket_r_o"], d["jacket_r_i"], d["jacket_top_z"], 0)
    jacket += Pos(0, 0, d["jacket_top_z"]) * Cylinder(d["jacket_r_o"], p["jacket_t"], align=B)
    jacket -= rod(ro, p["jacket_t"] + 2, 0, -a, d["jacket_top_z"] - 1)
    jacket -= rod(ro, p["jacket_t"] + 2, 0, a, d["jacket_top_z"] - 1)
    out["jacket"] = jacket

    # Dilution stack over the outlet leg, and the inlet blower
    out["stack"] = tube(p["stack_d"] / 2, p["stack_d"] / 2 - 0.6, p["stack_len"], d["stack_z0"], 0, a)
    bx, by, bz = p["blower"]
    out["blower"] = Pos(0, -a - by / 2 + ro, d["leg_top_z"]) * Box(bx, by, bz, align=B)

    names = ["bricks", "base_wool", "drum", "lid", "wells", "heaters", "utube", "sand",
             "insulation", "jacket", "stack", "blower"]
    assy = Compound([out[n] for n in names])
    return (assy, out) if parts else assy


if __name__ == "__main__":
    from build123d import export_step, export_stl
    part = build()
    out = Path(__file__).resolve().parents[1]
    export_step(part, str(out / "step" / "thermabrick-test-article.step"))
    export_stl(part, str(out / "stl" / "thermabrick-test-article.stl"))
    d = derived()
    print(f"sand depth {d['sand_depth']:.0f} mm, overall {d['overall_d']:.0f} dia x {d['overall_h']:.0f} mm high")
