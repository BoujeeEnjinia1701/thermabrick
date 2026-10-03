"""ThermaBrick prototype build plan pictures (TBK-BLD-001, STANDARDS section 18).

Run from the repo root:  python cad/src/build_plan_media.py [overview|sheets|layouts|joints|steps|wiring|labels ...]
With no argument it draws everything. Every picture is drawn from cad/src/model.py (build), so the
pictures and the model never disagree:
    docs/05-build-plan/overview.png        every component pulled apart, numbered in build order
    cad/drawings/TBK-DWG-101 to 110        making sketches for the made and drilled components
    docs/05-build-plan/*-layout.png        full-size hole and cutting layouts (matplotlib)
    docs/05-build-plan/joint-NN.png        close-ups of the joints that need explaining
    docs/05-build-plan/step-NN.png         one picture per assembly step
    docs/05-build-plan/wiring.png          block-level wiring and the safety chain (matplotlib)
    docs/05-build-plan/step-22.png         warning label positions (matplotlib)
Uses .kit/build_views.py. BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT. Licensed MIT.
"""
import sys
from math import cos, sin, radians, hypot, degrees, atan2
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / ".kit"), str(ROOT / "cad" / "src")]
import build_views as bv  # noqa: E402
from build_views import Part  # noqa: E402
from model import PARAMS as P, build, derived, thermocouples, _polar  # noqa: E402

OUT = ROOT / "docs" / "05-build-plan"
DWG = ROOT / "cad" / "drawings"
DATE = "2026-09-30"
D = derived(P)
_, C = build(parts=True)

COL = {"board": "#A8A48A", "ifb": "#D9C3A0", "aes": "#F2EFE8", "ring": "#8F8B70", "drum": "#4B5563",
       "wells": "#1F2937", "utubes": "#7C2D12", "tc": "#0E7490", "template": "#C08A4A", "sand": "#E3C68E",
       "head": "#E7E1CF", "lid": "#6B7280", "collector": "#111827", "heaters": "#DC2626", "side": "#B8B394",
       "jacket": "#9CA3AF", "top": "#C9C3A4", "cap": "#94A3B8", "trim": "#1F2937", "plenum": "#0F766E",
       "jbox": "#6D28D9", "rivet": "#D1D5DB", "duct": "#374151", "fan": "#1D4ED8", "damper": "#B45309"}


def part(name, key_or_shape, color, explode=(0, 0, 0), alpha=1.0):
    shape = C[key_or_shape] if isinstance(key_or_shape, str) else key_or_shape
    return Part(name, shape, color, None, tuple(explode), alpha)


def fuse(*ks):
    out = None
    for k in ks:
        s = C[k] if isinstance(k, str) else k
        out = s if out is None else out + s
    return out


def quarter(shape):
    """Remove the quadrant facing the camera (x > 0, y < 0) so the inside shows."""
    from build123d import Box, Pos
    big = 5000
    return shape - Pos(big / 2, -big / 2, big / 2 - 50) * Box(big, big, big)


def win(shape, x0, x1, y0, y1, z0, z1):
    from build123d import Box, Pos
    return shape & (Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0))


# ----------------------------------------------------------------- installation parts (simple shapes)
def air_path():
    """Inlet damper with servo on the plenum collar, hot outlet heat trap, mixing tee and fan.
    The route follows the appearance layout of product_model.py (an illustrative site layout)."""
    from build123d import Cylinder, Box, Pos, Rot, Align
    B = (Align.CENTER, Align.CENTER, Align.MIN)
    zc = D["cap_top_z"] + P["inlet_plenum_h"] / 2
    r_out = P["leg_outer_r"] + 45 + 117
    damper = Pos(r_out, 0, zc) * Rot(0, 90, 0) * Cylinder(P["outlet_d"] / 2 + 1.5, 110, align=B)
    servo = Pos(r_out + 55, 0, zc + 62) * Box(40, 20, 38)
    a = radians(35.0)
    rd, top = 800.0, 1640.0
    zt = D["overall_h"]
    r4 = P["outlet_d"] / 2
    rise = Cylinder(r4, top - zt + r4, align=B).moved(Pos(0, 0, zt))
    run = Pos(rd / 2 * cos(a), rd / 2 * sin(a), top) * Rot(0, 0, 35) * Rot(0, 90, 0) * Cylinder(r4, rd)
    drop = Pos(rd * cos(a), rd * sin(a), 1150.0) * Cylinder(r4, top - 1150.0, align=B)
    tee = Pos(rd * cos(a), rd * sin(a), 1150.0) * Rot(0, 0, 35) * Rot(0, 90, 0) * Cylinder(r4 + 3, 160)
    fanb = Pos(rd * cos(a), rd * sin(a), 765.0) * Cylinder(118, 230, align=B)
    feed = Pos(rd * cos(a), rd * sin(a), 995.0) * Cylinder(r4, 1150.0 - 995.0, align=B)
    return {"damper": damper + servo, "hot": rise + run + drop, "tee": tee + feed, "fan": fanb}


AIR = air_path()


# ----------------------------------------------------------------- named components, in build order
def made():
    return {
        "boards": part("Stone wool base boards (2 layers)", fuse("base_board_1", "base_board_2"), COL["board"]),
        "ifb": part("Firebrick disc", "base_ifb", COL["ifb"]),
        "aes": part("AES board disc", "base_aes", COL["aes"]),
        "ring": part("Batt ring round the disc", "base_ring", COL["ring"]),
        "drum": part("Drum, prepared", "drum", COL["drum"]),
        "wells": part("Heater wells (12)", "wells", COL["wells"]),
        "utubes": part("U-tubes (6)", "utubes", COL["utubes"]),
        "tc": part("Thermocouples and guide rods", fuse("thermocouples", "tc_guides"), COL["tc"]),
        "template": part("Setting template (removed after the fill)", "template", COL["template"]),
        "sand": part("Sand, 210 kg", "sand", COL["sand"]),
        "head": part("Headspace insulation", "ins_head", COL["head"]),
        "lid": part("Drum lid, drilled, and ring", "lid", COL["lid"]),
        "collector": part("Collector and outlet", fuse("collector", "collector_rivets"), COL["collector"]),
        "heaters": part("Cartridge heaters (12)", "heaters", COL["heaters"]),
        "side": part("Side insulation", "ins_side", COL["side"]),
        "jacket": part("Jacket side", "jacket", COL["jacket"]),
        "top": part("Top insulation", "ins_top", COL["top"]),
        "cap": part("Jacket cap", "jacket_cap", COL["cap"]),
        "trim": part("Outlet packing and trim ring", fuse("outlet_packing", "trim_ring"), COL["trim"]),
        "plenum": part("Inlet plenum", "inlet_plenum", COL["plenum"]),
        "jbox": part("Heater junction box", "jbox", COL["jbox"]),
    }


ORDER = ["boards", "ifb", "aes", "ring", "drum", "wells", "utubes", "tc", "template", "sand", "head", "lid",
         "collector", "heaters", "side", "jacket", "top", "cap", "trim", "plenum", "jbox"]


# ----------------------------------------------------------------- overview
def overview():
    M = made()
    sr = (cos(radians(32)), sin(radians(32)))     # screen right at azimuth -58

    def o(col, z):
        return (col * sr[0], col * sr[1], z)
    off = {"boards": o(-2100, 0), "ifb": o(-2100, 300), "aes": o(-2100, 520), "ring": o(-2100, 760),
           "side": o(-2100, 1250),
           "drum": o(-700, 0), "wells": o(-950, 1100), "utubes": o(-450, 1500), "tc": o(-700, 1250),
           "template": o(-700, 2250),
           "sand": o(700, 0), "head": o(700, 300), "lid": o(700, 520), "collector": o(700, 700),
           "heaters": o(700, 1700),
           "jacket": o(2100, 0), "top": o(2100, 650), "cap": o(2100, 1000), "trim": o(2100, 1150),
           "plenum": o(2100, 1300), "jbox": o(2100, 1500)}
    parts = []
    for k in ORDER:
        p = M[k]
        p.explode = off[k]
        parts.append(p)
    return bv.overview(parts, OUT / "overview.png", "ThermaBrick prototype: every component, pulled apart",
                       subtitle="Numbered in build order, in four columns: base, drum and pipes, what goes in and on the drum, the jacket. "
                                "The template (9) is a temporary jig",
                       elev=14, azim=-58, size=(14, 8.5), dpi=150, key=True)


# ----------------------------------------------------------------- making sketches
def sheets():
    from build123d import Pos, Rot
    M = made()
    base = dict(project="ThermaBrick", date=DATE)
    out = []
    zf = D["floor_z"]
    dq = part("Drum, cut open", quarter(C["drum"]), COL["drum"])

    # 101 base
    out.append(bv.component_sheet(
        part("Base", "base", COL["ifb"]), [M["drum"]],
        dwg_no="TBK-DWG-101", title="ThermaBrick base: making sketch",
        material="Stone wool board 50 mm; K-23 firebrick; AES board 25 mm; stone wool batt 89 mm",
        inset_view=(18, -58),
        notes=["Four layers, 189 mm in all, 1,208 mm across (the inside of the jacket).",
               "Boards: two layers of 50 mm stone wool board, each from two 610 x 1,219 mm",
               "  boards butted into a 1,219 mm square and cut to a 1,208 mm disc.",
               "  Turn the top layer 90 degrees so the joints cross.",
               "Firebrick: one course laid flat (64 mm), 610 mm disc in the middle,",
               "  bricks in staggered rows, cut with a saw to the circle (layout picture).",
               "AES board: one 25 mm board cut to a 610 mm disc, laid on the bricks.",
               "Ring: 89 mm stone wool batt cut into segments to fill from the 610 mm disc",
               "  out to 1,208 mm, level with the top of the AES board.",
               "Fit: the drum's bottom rim (597 mm) stands on the AES disc, 6 mm in from",
               "  its edge, over the firebrick, which carries the load.",
               "Check: the top is flat within 3 mm across a straight edge."],
        **base))

    # 102 drum lid, drilled
    out.append(bv.component_sheet(
        part("Drum lid", "lid", COL["lid"]), [M["drum"], M["wells"], M["utubes"]],
        dwg_no="TBK-DWG-102", title="ThermaBrick drum lid: drilling sketch",
        material="The drum's own 16 ga steel lid and bolted closing ring",
        view_shape=Pos(0, 0, -D["lid_z"]) * C["lid"], inset_view=(30, -58),
        notes=["Drill the lid with the template (TBK-DWG-103) clamped on it as a guide.",
               "Twelve 36 mm holes for the heater wells: six on a 150 mm radius at",
               "  0, 60, 120 ... degrees and six on a 245 mm radius at the same angles.",
               "Twelve 48 mm holes for the U-tube legs: six on 80 mm and six on 235 mm",
               "  radius at 30, 90, 150 ... degrees (between the wells).",
               "Four 6 mm holes for the sand thermocouples (lid layout picture).",
               "Cut with bi-metal hole saws at low speed with cutting oil; deburr.",
               "Mark a line at 0 degrees on the lid and the drum rim to line them up.",
               "Fit: the lid drops over all 24 pipe ends, the well holes leaving a",
               "  4.6 mm gap (a T1 to T3 sheath fits beside its well) and the leg holes",
               "  2.9 mm. An AES rope collar is laid round every pipe on the lid.",
               "Check: lay the template on the lid; every hole lines up."],
        **base))

    # 103 setting template
    out.append(bv.component_sheet(
        part("Setting template", "template", COL["template"]), [M["drum"], M["wells"], M["utubes"]],
        dwg_no="TBK-DWG-103", title="ThermaBrick setting template: making sketch",
        material="Exterior plywood 18 mm", view_shape=Pos(0, 0, -D["lid_z"]) * C["template"], inset_view=(30, -58),
        notes=["A temporary jig. Cut a 597 mm disc from 18 mm plywood: it sits on the",
               "  drum's top rim, where the lid will go.",
               "Drill the same holes as the lid (36 mm wells, 48 mm legs, 6 mm sheaths)",
               "  from the lid layout picture, with the 0 degree line marked.",
               "Pour holes: one 80 mm hole in the centre and four 64 mm holes on a",
               "  200 mm radius at 15, 105, 195 and 285 degrees.",
               "Drill the template first and use it to drill the lid, so both match.",
               "Fit: the template drops over the pipe ends and holds every well,",
               "  U-tube leg and sheath upright while sand is poured through the pour",
               "  holes. Lift it off before the headspace insulation goes in.",
               "Check: it lies flat on the rim with all 24 pipes through it."],
        **base))

    # 104 heater well
    x, y = _polar(P["heater_rings"][0], 0)
    out.append(bv.component_sheet(
        part("Heater well", _one_well(), COL["wells"]), [dq, M["utubes"]],
        dwg_no="TBK-DWG-104", title="ThermaBrick heater well (make 12): making sketch",
        material="Black steel pipe 3/4 in Sch 40 (26.7 mm), malleable iron cap 3/4 in NPT",
        view_shape=Pos(-x, -y, -zf) * _one_well(), inset_view=(20, -58),
        notes=[f"Cut twelve lengths of {D['well_len']:.0f} mm from four 10 ft pipes (three per pipe).",
               "Thread one end 3/4 in NPT (rented pipe threader); ream and deburr.",
               "Clean off cutting oil with degreaser: oil smokes on first heat.",
               "Coat the thread with nickel anti-seize (no PTFE tape or paste) and",
               "  screw on the cap hand tight plus one and a half turns.",
               "The open top end is square cut and deburred so a heater slides in.",
               "Fit: the cap stands on a levelled 14 mm first lift of sand; the template",
               "  and then the lid hold the top, which ends 25 mm above the lid.",
               "Each 508 mm heater rests on the cap inside, its heated part 26 to",
               "  483 mm above the drum floor; its leads rise out of the open top.",
               f"Check: length {D['well_len']:.0f} mm plus cap, within 3 mm; a 16 mm rod slides",
               "  to the bottom freely."],
        **base))

    # 105 U-tube
    u = _one_utube()
    ang = P["utube_angle0"]
    out.append(bv.component_sheet(
        part("U-tube", u, COL["utubes"]), [dq, M["wells"]],
        dwg_no="TBK-DWG-105", title="ThermaBrick U-tube (make 6): making sketch",
        material="Black steel pipe 1-1/4 in Sch 40; two 90 degree elbows; 1-1/4 x 4 in nipple",
        view_shape=Pos(0, 0, -zf) * (Rot(0, 0, -ang) * u), inset_view=(20, -58),
        notes=[f"Cut six inlet legs {D['inlet_leg_len']:.0f} mm long (two per 10 ft pipe) and six",
               f"  outlet legs {D['outlet_leg_len']:.0f} mm (three per pipe). Thread one end of each.",
               "Degrease, coat every thread with nickel anti-seize, then join:",
               "  outlet leg, elbow, 4 in nipple, elbow, inlet leg, wrench tight.",
               "Turn the second elbow so both legs stand parallel, in one plane.",
               "Leg centres 155 mm apart (the fittings make 155.6 mm).",
               "The elbows rest on the drum floor; the run is 28 mm above it.",
               "Fit: the short leg (outlet) stands on the 80 mm circle and ends inside",
               "  the collector; the long leg (inlet) on the 235 mm circle, ending",
               "  inside the inlet plenum, 130 mm above the jacket cap.",
               "Check: legs parallel within 3 mm over their length; blow through",
               "  it to clear swarf."],
        **base))

    # 106 collector
    out.append(bv.component_sheet(
        part("Collector", fuse("collector", "collector_rivets"), COL["collector"]), [M["lid"], M["wells"], M["utubes"]],
        dwg_no="TBK-DWG-106", title="ThermaBrick collector and outlet: making sketch",
        material="10 in black stovepipe 24 ga; 18 ga steel sheet; 4 in start collar and pipe",
        view_shape=Pos(0, 0, -D["top_ins_z0"]) * C["collector"], inset_view=(28, -58),
        notes=["Ring: cut an 80 mm band from 10 in (254 mm) black stovepipe.",
               "Tabs: at the foot, at 30, 90, 150 ... degrees, cut six slits 20 mm deep",
               "  and 20 mm apart and fold the tabs out flat. Drill each for a 4.8 mm",
               "  steel rivet, 10 mm from the ring.",
               "Top: cut a 266 mm disc from 18 ga uncoated steel, fold a 12 mm edge",
               "  down over the ring and rivet it in six places.",
               "Cut a 4 in hole in the middle and rivet in the 4 in crimped start",
               "  collar; fit the 4 in pipe to 160 mm above the jacket cap.",
               "Drill a 4 mm hole 95 mm from the centre for thermocouple T8.",
               "Fit: tabs riveted to the lid between the inner wells; AES rope pressed",
               "  round the foot of the ring. The six short legs end inside it.",
               "No zinc: use uncoated steel and steel rivets only."],
        **base))

    # 107 jacket side
    out.append(bv.component_sheet(
        part("Jacket side", "jacket", COL["jacket"]), [M["cap"], M["side"]],
        dwg_no="TBK-DWG-107", title="ThermaBrick jacket side: making sketch",
        material="Galvanized steel flashing 0.6 mm, 610 mm wide coil",
        inset_view=(18, -58),
        notes=["Three rows of 610 mm flashing, each 3,850 mm long (3,800 mm round",
               "  plus a 50 mm lap), wrapped round the side insulation.",
               "Bottom row on the floor; the second laps 25 mm outside it; the top",
               "  row is cut to width so the side ends 1,302 mm above the floor.",
               "Pull each row tight with ratchet straps over the insulation, then",
               "  rivet the vertical lap every 100 mm with 4.8 mm aluminium rivets.",
               "Rivet the row laps every 150 mm. Stagger the vertical laps.",
               "Inside diameter 1,208 mm: the insulation is 317 mm thick all round.",
               "Fit: the cap's 25 mm skirt sits outside the top row and is held by",
               "  sheet metal screws (not rivets) so the cap can come off.",
               "The jacket runs at about 26 degrees C, so galvanized steel is fine.",
               "Check: round within 10 mm on two diameters; no gaps at the laps."],
        **base))

    # 108 jacket cap
    out.append(bv.component_sheet(
        part("Jacket cap", "jacket_cap", COL["cap"]), [M["jacket"], M["plenum"], M["jbox"]],
        dwg_no="TBK-DWG-108", title="ThermaBrick jacket cap: making sketch",
        material="Galvanized steel flashing 0.6 mm, 610 mm wide coil",
        view_shape=Pos(0, 0, -D["jacket_top_z"]) * C["jacket_cap"], inset_view=(35, -58),
        notes=["Three strips of 610 mm flashing, 1,260 mm long, lapped 25 mm and",
               "  riveted into one sheet; cut a 1,260 mm disc.",
               "Snip the edge every 50 mm, 25 mm deep, and turn it down 90 degrees",
               "  to make the skirt (1,210 mm inside).",
               "Holes (cap layout picture): 180 mm in the centre for the outlet; six",
               "  46 mm on a 235 mm radius at 30, 90 ... degrees for the inlet legs;",
               "  40 mm at 120 degrees, 430 mm out, under the junction box; 25 mm at",
               "  95 degrees, 330 mm out, for the thermocouple exit.",
               "Fit grommets in the 40 and 25 mm holes; foil tape round the legs.",
               "Fit: it lowers over the six inlet legs and the outlet and rests on the",
               "  top insulation; eight screws through the skirt into the side.",
               "Check: every hole lines up with its pipe before it is pressed down."],
        **base))

    # 109 trim ring
    out.append(bv.component_sheet(
        part("Outlet trim ring", "trim_ring", COL["trim"]), [M["cap"], M["collector"]],
        dwg_no="TBK-DWG-109", title="ThermaBrick outlet trim ring: making sketch",
        material="Uncoated (black) steel sheet 18 ga (1.2 mm)",
        view_shape=Pos(0, 0, -D["cap_top_z"]) * C["trim_ring"], inset_view=(35, -58),
        notes=["Cut a 250 mm disc from 18 ga uncoated steel with snips; file the edge.",
               "Cut a 106 mm hole in the middle (2.3 mm clear of the 4 in pipe).",
               "Drill four 3.5 mm holes on a 230 mm circle for sheet metal screws.",
               "Fit: the 180 mm hole in the galvanized cap leaves a 39 mm gap round the",
               "  hot outlet. Pack the gap with AES blanket (20 mm deep), then lay the",
               "  ring over it and screw it to the cap at its outer edge.",
               "The ring, not the cap, faces the hot pipe, so no zinc sits within",
               "  39 mm of it (requirement R13: no zinc above 200 degrees C).",
               "Check: the ring does not touch the pipe at any point."],
        **base))

    # 110 inlet plenum
    out.append(bv.component_sheet(
        part("Inlet plenum", "inlet_plenum", COL["plenum"]), [M["cap"], M["utubes"], M["jbox"]],
        dwg_no="TBK-DWG-110", title="ThermaBrick inlet plenum: making sketch",
        material="Galvanized steel flashing 0.6 mm; 4 in crimped start collar",
        view_shape=Pos(0, 0, -D["cap_top_z"]) * C["inlet_plenum"], inset_view=(30, -58),
        notes=["An annular box 140 mm high, 380 mm inside and 560 mm outside.",
               "Walls: strips 170 mm wide (140 high plus a 15 mm flange and a 15 mm",
               "  tab edge), 1,780 mm long for the outer wall and 1,220 mm for the inner,",
               "  rolled round and riveted at a 25 mm lap.",
               "Top: an annulus 560 mm outside, 380 mm inside, from flashing.",
               "Snip the tab edges every 40 mm, fold them over the top and rivet.",
               "Snip the foot edges and fold them out (outer wall) and in (inner wall)",
               "  as 15 mm flanges.",
               "Collar: cut a 4 in hole in the outer wall at 0 degrees, centred 70 mm",
               "  up, and rivet in the crimped start collar (19 mm of wall each side).",
               "Fit: flanges riveted to the cap; the six inlet legs end 10 mm below",
               "  the top inside it. Seal the flanges with foil tape."],
        **base))
    return out


def _one_well():
    from build123d import Pos, Cylinder, Align
    B = (Align.CENTER, Align.CENTER, Align.MIN)
    x, y = _polar(P["heater_rings"][0], 0)
    w_z0 = D["well_z0"]
    h = D["well_len"]
    w = Pos(x, y, w_z0 - 6) * Cylinder(P["well_cap_od"] / 2, P["well_cap_h"], align=B)
    w += Pos(x, y, w_z0) * Cylinder(P["well_od"] / 2, h, align=B)
    w -= Pos(x, y, w_z0 + 6) * Cylinder(P["well_id"] / 2, h, align=B)
    return w


def _one_utube():
    return C["utubes"].solids()[0]


# ----------------------------------------------------------------- layouts (matplotlib)
INK, MUT, AC = "#111827", "#4B5563", "#0F766E"


def _fig(w, h, title, sub):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(w, h), dpi=150)
    fig.text(0.03, 0.975, title, fontsize=13, fontweight="bold", color=INK, va="top")
    fig.text(0.03, 0.94, sub, fontsize=8.5, color=MUT, va="top")
    fig.text(0.03, 0.015, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    fig.text(0.97, 0.015, "github.com/BoujeeEnjinia1701/thermabrick", fontsize=7, color=AC, ha="right", family="monospace")
    return fig, plt


def layouts():
    from matplotlib.patches import Circle, Rectangle, Polygon
    res = []
    # ---- lid and template layout
    fig, plt = _fig(11, 9.5, "Drum lid and setting template: hole layout",
                    "Seen from above. Radius from the centre and angle from the 0 degree mark, anticlockwise. "
                    "Template only: the four 64 mm and the 80 mm pour holes (dashed).")
    ax = fig.add_axes([0.03, 0.06, 0.62, 0.84]); ax.set_aspect("equal"); ax.set_axis_off()
    R = P["chime_od"] / 2
    ax.add_patch(Circle((0, 0), R, fc="#F3F4F6", ec=INK, lw=1.2))
    for r in (80, 150, 235, 245):
        ax.add_patch(Circle((0, 0), r, fc="none", ec=MUT, lw=0.4, ls=":"))
    for a in range(0, 360, 30):
        ax.plot([0, (R + 6) * cos(radians(a))], [0, (R + 6) * sin(radians(a))], color=MUT, lw=0.3, ls=":")
        ax.text((R + 22) * cos(radians(a)), (R + 22) * sin(radians(a)), f"{a}°", ha="center", va="center", fontsize=7.5, color=MUT)
    for x, y, dia in C["_holes"]:
        fc = {36.0: "white", 48.0: "white", 6.0: "#0E7490"}[dia]
        ax.add_patch(Circle((x, y), dia / 2, fc=fc, ec=INK, lw=1))
    pd, pr, pa, pc = P["pour_holes"]
    for a in pa:
        ax.add_patch(Circle(_polar(pr, a), pd / 2, fc="none", ec=P and "#B45309", lw=1, ls="--"))
    ax.add_patch(Circle((0, 0), pc / 2, fc="none", ec="#B45309", lw=1, ls="--"))
    tags = {}
    for tag, xy, tip, cross in thermocouples():
        if cross == "well":
            tags[tag] = xy
        elif isinstance(cross, tuple):
            tags[tag] = cross
        else:
            tags[tag] = xy
    for tag, (x, y) in tags.items():
        r, a0 = hypot(x, y), degrees(atan2(y, x))
        lx, ly = _polar(r + 26, a0 + (9 if tag != "T4" else -2))
        if tag in ("T1", "T2", "T3"):
            lx, ly = _polar(r + (22 if tag != "T2" else -60), a0 + 9)
        ax.plot([x, lx], [y, ly], color="#0E7490", lw=0.6)
        ax.text(lx, ly, tag, fontsize=7.5, color="#0E7490", ha="center", va="center", fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
    ax.plot([0, R], [0, 0], color=AC, lw=1.2)
    ax.text(R - 45, -30, "0° mark", color=AC, fontsize=8, ha="center", va="top")
    ax.set_xlim(-R - 40, R + 40); ax.set_ylim(-R - 40, R + 40)
    key = ["Heater wells: twelve 36 mm holes", "  6 on 150 mm radius at 0, 60, 120 ...",
           "  6 on 245 mm radius at 0, 60, 120 ...", "U-tube legs: twelve 48 mm holes",
           "  6 on 80 mm radius at 30, 90, 150 ...", "  6 on 235 mm radius at 30, 90, 150 ...",
           "Sand thermocouples: four 6 mm holes", "  T4 165 mm at 51°", "  T5 200 mm at 45°", "  T6 270 mm at 45°",
           "  T7 200 mm at 225°", "T1, T2, T3 pass through their well's", "  hole, beside the well (T1 at 0°,",
           "  T2 at 180° outer ring, T3 at 120°)", "", "Template pour holes (template only):",
           "  80 mm in the centre", "  64 mm on 200 mm radius at", "  15, 105, 195, 285°"]
    fig.text(0.67, 0.86, "What each hole is", fontsize=9.5, fontweight="bold", color=INK, va="top")
    for i, t in enumerate(key):
        fig.text(0.67, 0.83 - i * 0.026, t, fontsize=8.2, color=INK, va="top")
    fig.savefig(OUT / "lid-layout.png", facecolor="white"); plt.close(fig); res.append(OUT / "lid-layout.png")

    # ---- jacket cap layout
    fig, plt = _fig(11, 9.5, "Jacket cap: hole layout and what sits on it",
                    "Seen from above. Solid: holes to cut. Dashed: outlines of the parts that sit on the cap.")
    ax = fig.add_axes([0.03, 0.06, 0.62, 0.84]); ax.set_aspect("equal"); ax.set_axis_off()
    R = D["jacket_r_o"]
    ax.add_patch(Circle((0, 0), R, fc="#F3F4F6", ec=INK, lw=1.2))
    ax.add_patch(Circle((0, 0), P["outlet_hole_d"] / 2, fc="white", ec=INK, lw=1))
    ax.add_patch(Circle((0, 0), P["outlet_d"] / 2, fc="#374151", ec=INK, lw=0.6))
    ax.add_patch(Circle((0, 0), P["trim_ring"][0] / 2, fc="none", ec=MUT, lw=0.8, ls="--"))
    for i in range(6):
        x, y = _polar(P["leg_outer_r"], 30 + 60 * i)
        ax.add_patch(Circle((x, y), P["cap_tube_hole"] / 2, fc="white", ec=INK, lw=1))
    for r in (190 - 15, 190, 280, 295):
        ax.add_patch(Circle((0, 0), r, fc="none", ec=AC, lw=0.6, ls="--"))
    ja, jr, jx, jy, jh = P["jbox"]
    cx, cy = _polar(jr, ja)
    a = radians(ja)
    corners = [(cx + u * cos(a) - v * sin(a), cy + u * sin(a) + v * cos(a)) for u, v in ((-jx / 2, -jy / 2), (jx / 2, -jy / 2), (jx / 2, jy / 2), (-jx / 2, jy / 2))]
    ax.add_patch(Polygon(corners, fc="none", ec="#6D28D9", lw=0.9, ls="--"))
    ax.add_patch(Circle((cx, cy), P["jbox_hole"] / 2, fc="white", ec=INK, lw=1))
    ex, ey = _polar(P["tc_exit"][1], P["tc_exit"][0])
    ax.add_patch(Circle((ex, ey), P["tc_exit"][2] / 2, fc="white", ec=INK, lw=1))
    ax.add_patch(Rectangle((280, -50.8), 117, 101.6, fc="none", ec=AC, lw=0.6, ls="--"))
    lab = [((0, -P["outlet_hole_d"] / 2 - 8), "180 mm hole, outlet\n(trim ring 250 mm, dashed)", "top"),
           (_polar(P["leg_outer_r"] + 75, 270), "inlet legs: six 46 mm\non 235 mm radius", "top"),
           ((cx, cy - jy / 2 - 30), "junction box 150 x 150,\n40 mm hole at 120°, 430 mm", "top"),
           ((ex + 95, ey + 18), "thermocouple exit,\n25 mm at 95°, 330 mm", "bottom"),
           ((420, 58), "plenum and 4 in collar\nat 0° (dashed)", "bottom")]
    for (x, y), t, va in lab:
        ax.text(x, y, t, fontsize=7.6, color=INK, ha="center", va=va, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
    ax.plot([0, R], [0, 0], color=AC, lw=0.6, ls=":")
    ax.text(R - 30, -12, "0°", color=AC, fontsize=8)
    ax.set_xlim(-R - 20, R + 20); ax.set_ylim(-R - 20, R + 20)
    key = ["Cap 1,260 mm blank, skirt turned down", "  25 mm (1,210 mm inside)", "",
           "Holes:", "  180 mm centre (outlet, packed with AES,", "    covered by the black steel trim ring)",
           "  six 46 mm on 235 mm radius at 30, 90 ...", "  40 mm at 120°, 430 mm out (heater leads,", "    grommet, under the junction box)",
           "  25 mm at 95°, 330 mm out (thermocouple", "    exit, grommet)", "",
           "Sits on the cap:", "  inlet plenum, 380 to 560 mm across,", "    flanges 350 to 590 mm",
           "  junction box at 120°, 430 mm out", "  trim ring over the centre hole"]
    fig.text(0.67, 0.86, "Cap holes and parts", fontsize=9.5, fontweight="bold", color=INK, va="top")
    for i, t in enumerate(key):
        fig.text(0.67, 0.83 - i * 0.026, t, fontsize=8.2, color=INK, va="top")
    fig.savefig(OUT / "cap-layout.png", facecolor="white"); plt.close(fig); res.append(OUT / "cap-layout.png")

    # ---- firebrick disc layout
    fig, plt = _fig(10, 8.8, "Firebrick disc: cutting layout",
                    "Seen from above. K-23 bricks 230 x 114 x 64 mm laid flat in staggered rows and cut to a 610 mm circle. "
                    "Numbers are the bricks each piece is cut from.")
    ax = fig.add_axes([0.05, 0.06, 0.62, 0.82]); ax.set_aspect("equal"); ax.set_axis_off()
    rc = P["base_core_d"] / 2
    pieces = sorted(C["base_ifb"].solids(), key=lambda s: -s.bounding_box().size.X)
    bins = []
    for s in pieces:
        L = s.bounding_box().size.X + 2
        for i, free in enumerate(bins):
            if free >= L + 3:
                bins[i] = free - L - 3; s._brick = i + 1; break
        else:
            bins.append(P["brick"][0] - L - 3); s._brick = len(bins)
    for s in pieces:
        bb = s.bounding_box()
        f = [f for f in s.faces() if abs(f.normal_at().Z - 1) < 1e-6]
        pts = [(v.X, v.Y) for v in (f[0].outer_wire().edges() and f[0].outer_wire().vertices())] if f else []
        from matplotlib.patches import Polygon as Pg
        try:
            poly = [(p.X, p.Y) for p in f[0].outer_wire().positions([i / 60 for i in range(61)])]
            ax.add_patch(Pg(poly, fc="#E9DCC4", ec=INK, lw=0.8))
        except Exception:
            ax.add_patch(Rectangle((bb.min.X, bb.min.Y), bb.size.X, bb.size.Y, fc="#E9DCC4", ec=INK, lw=0.8))
        ax.text(bb.center().X, bb.center().Y, str(s._brick), fontsize=8, ha="center", va="center", color=INK)
    ax.add_patch(Circle((0, 0), rc, fc="none", ec=AC, lw=1.2, ls="--"))
    ax.add_patch(Circle((0, 0), P["chime_od"] / 2, fc="none", ec="#B91C1C", lw=0.8, ls=":"))
    ax.set_xlim(-rc - 20, rc + 20); ax.set_ylim(-rc - 20, rc + 20)
    key = [f"{len(pieces)} pieces from {len(bins)} bricks;", "  buy 16 (one spare).", "",
           "Lay the rows on the stone wool", "  board, joints staggered by half", "  a brick, 2 mm joints, no mortar.",
           "", "Mark the 610 mm circle (dashed)", "  with a trammel and saw to it", "  with a coarse handsaw or a", "  masonry blade, outdoors, with",
           "  a P100 or N95 respirator.", "", "Red dotted: the drum's 597 mm", "  bottom rim, which stands on", "  the AES disc above the bricks."]
    for i, t in enumerate(key):
        fig.text(0.70, 0.84 - i * 0.03, t, fontsize=8.4, color=INK, va="top")
    fig.savefig(OUT / "brick-layout.png", facecolor="white"); plt.close(fig); res.append(OUT / "brick-layout.png")
    return res


# ----------------------------------------------------------------- joints
def joints():
    out = []
    zf, zl, zt, ct = D["floor_z"], D["lid_z"], D["jacket_top_z"], D["cap_top_z"]
    zb = D["base_h"]

    def J(n, items, title, sub, elev, azim, size=(8, 6)):
        out.append(bv.joint([p for p in items], OUT / f"joint-{n:02d}.png", f"Joint {n}: {title}", subtitle=sub,
                            elev=elev, azim=azim, size=size))

    b = (200, 380, 0, 30, 30, 320)
    J(1, [part("Stone wool boards", win(fuse("base_board_1", "base_board_2"), *b), COL["board"]),
          part("Firebrick disc", win(C["base_ifb"], *b), COL["ifb"]),
          part("AES board disc", win(C["base_aes"], *b), COL["aes"]),
          part("Batt ring", win(C["base_ring"], *b), COL["ring"]),
          part("Drum bottom rim and wall", win(C["drum"], *b), COL["drum"]),
          part("Side insulation", win(C["ins_side"], *b), COL["side"])],
      "the drum on the base (cut open at the edge)",
      "Seen from the front. The drum's rim stands on the AES disc over the firebrick; the batt ring fills out to the jacket",
      3, -90)
    b = (110, 190, 0, 40, zf - 30, zf + 70)
    J(2, [part("Drum floor", win(C["drum"], *b), COL["drum"]),
          part("Sand; its first 14 mm lift is levelled under the cap", win(C["sand"], *b), COL["sand"]),
          part("Well cap", win(C["wells"], *b), COL["wells"]),
          part("Heater resting on the cap", win(C["heaters"], *b), COL["heaters"])],
      "heater well foot (cut through the well)",
      "The cap stands on a levelled 14 mm lift of sand, which keeps it off the drum floor; the heater rests in the cap", 10, -90)
    b = (0, 25, 40, 270, zf - 20, zf + 110)
    J(3, [part("Drum floor", win(C["drum"], *b), COL["drum"]),
          part("Elbows, 4 in nipple and legs", win(C["utubes"], *b), COL["utubes"])],
      "U-tube foot (cut through the tube)",
      "Two elbows and a 4 in nipple set the legs 155 mm apart; the elbows rest on the floor", 10, 180)
    x1 = P["heater_rings"][0]
    b = (x1 - 35, x1 + 40, 0, 40, zl - 50, zl + 50)
    J(4, [part("Lid (36 mm hole)", win(C["lid"], *b), COL["lid"]),
          part("Heater well", win(C["wells"], *b), COL["wells"]),
          part("Thermocouple T1 beside the well", win(C["thermocouples"], *b), COL["tc"]),
          part("Headspace insulation", win(C["ins_head"], *b), COL["head"])],
      "well and thermocouple through the lid (cut)",
      "The 36 mm hole passes the well and its sheath; an AES rope collar closes it on top", 12, -90)
    tx, ty = _polar(137, 30)
    b = (tx - 45, tx + 35, ty - 35, ty + 35, zl - 10, zl + 45)
    J(5, [part("Lid", win(C["lid"], *b), COL["lid"]),
          part("Collector ring and tab", win(C["collector"], *b), COL["collector"]),
          part("Steel rivet", win(C["collector_rivets"], *b), COL["rivet"])],
      "collector tab riveted to the lid",
      "Six tabs folded out at the foot of the ring, between the inner wells; one steel rivet each", 25, -60)
    b = (20, 145, 0, 30, zt - 35, ct + 22)
    J(6, [part("Outlet pipe (hot)", win(C["collector"], *b), COL["collector"]),
          part("Top insulation", win(C["ins_top"], *b), COL["top"]),
          part("AES packing", win(C["outlet_packing"], *b), COL["aes"]),
          part("Galvanized cap (39 mm clear)", win(C["jacket_cap"], *b), COL["cap"]),
          part("Black steel trim ring", win(C["trim_ring"], *b), COL["trim"])],
      "hot outlet through the jacket cap (cut)",
      "Section, seen from the front. The galvanized cap stops 39 mm from the hot pipe; AES packing fills the gap; the trim ring covers it", 3, -90)
    lx, ly = _polar(P["leg_outer_r"], 330)
    b = (150, 330, ly, ly + 90, zt - 40, ct + 160)
    J(7, [part("Inlet leg", win(C["utubes"], *b), COL["utubes"]),
          part("Jacket cap", win(C["jacket_cap"], *b), COL["cap"]),
          part("Top insulation", win(C["ins_top"], *b), COL["top"]),
          part("Inlet plenum, flanges riveted", win(C["inlet_plenum"], *b), COL["plenum"])],
      "inlet leg into the plenum (cut through the leg)",
      "The leg passes the cap and ends 10 mm below the plenum top; the flanges sit on the cap", 12, -90)
    cx, cy = _polar(P["jbox"][1], P["jbox"][0])
    b = (cx - 110, cx + 110, cy, cy + 110, zt - 40, ct + 110)
    from build123d import Pos as _P, Cylinder as _Cy
    leads = _P(cx, cy, (zt - 40 + ct + 60) / 2) * _Cy(9, ct + 60 - (zt - 40))
    J(8, [part("Jacket cap, 40 mm hole with grommet", win(C["jacket_cap"], *b), COL["cap"]),
          part("Top insulation", win(C["ins_top"], *b), COL["top"]),
          part("Heater leads (12 pairs)", win(leads, *b), COL["heaters"]),
          part("Junction box, cut open", win(C["jbox"], *b), COL["jbox"])],
      "junction box on the cap (cut)",
      "The heater leads rise through the top insulation and a grommet into the box; four screws hold it", 15, -90)
    x5, y5 = _polar(200, 45)
    b = (x5 - 20, x5 + 20, y5 - 20, y5 + 20, zf - 8, zf + 600)
    J(9, [part("Drum floor", win(C["drum"], *b), COL["drum"]),
           part("Thermocouple T5 sheath", win(C["thermocouples"], *b), COL["tc"]),
           part("Guide rod, tied with wire", win(C["tc_guides"], *b), "#6B7280")],
      "sand thermocouple on its guide rod",
      "The rod stands on the floor 7 mm from the sheath; tie them every 100 mm with stainless wire", 15, -40, size=(7, 6))
    return out


# ----------------------------------------------------------------- assembly steps
def steps(only=None):
    M = made()
    out = []
    Q = lambda p: Part(p.name, quarter(p.shape), p.color, None, p.explode, p.alpha)  # noqa: E731

    def mv(p, e, cut=False):
        q = Q(p) if cut else p
        return Part(q.name, q.shape, q.color, None, tuple(e), q.alpha)

    def st(n, done, new, title, sub, **kw):
        if only and n not in only:
            return
        kw.setdefault("elev", 22); kw.setdefault("azim", -58); kw.setdefault("label_done", False)
        out.append(bv.step(done, new, OUT / f"step-{n:02d}.png", f"Step {n}: {title}", subtitle=sub, **kw))

    st(1, [], [mv(part("Stone wool board, bottom layer", "base_board_1", COL["board"]), (0, 0, 150)),
               mv(part("Stone wool board, top layer (turned 90°)", "base_board_2", COL["ring"]), (0, 0, 300))],
       "stone wool boards on the slab", "Two layers, joints crossed, on a clean, level concrete slab", elev=25)
    bd = [M["boards"]]
    st(2, bd, [mv(M["ifb"], (0, 0, 200)), mv(M["aes"], (0, 0, 380)), mv(M["ring"], (0, 0, 120))],
       "firebrick disc, AES disc and batt ring", "Bricks to the cutting layout; AES board disc on top; batt segments round them, level", elev=25)
    base = [M["boards"], M["ifb"], M["aes"], M["ring"]]
    st(3, base, [mv(M["drum"], (0, 0, 500))], "drum onto the base",
       "Empty and prepared; centred on the AES disc, 0° mark on the rim facing the inlet side", elev=20)
    dq = [Q(p) for p in base + [M["drum"]]]
    st(4, dq, [mv(M["wells"], (0, 0, 650), cut=True)], "heater wells into the drum",
       "Level a 14 mm first lift of sand; stand each capped well on it at its mark; tape over the open tops", elev=30)
    st(5, dq + [Q(M["wells"])], [mv(M["utubes"], (0, 0, 700), cut=True)], "U-tubes into the drum",
       "Elbows on the floor, short legs on the 80 mm circle, long legs on the 235 mm circle; tape the tops", elev=30)
    st(6, dq + [Q(M["wells"]), Q(M["utubes"])], [mv(M["tc"], (0, 0, 500), cut=True)], "thermocouples and guide rods",
       "T1 to T3 wired to their wells; T4 to T7 tied to guide rods standing on the floor", elev=30)
    inner = dq + [Q(M["wells"]), Q(M["utubes"]), Q(M["tc"])]
    st(7, inner, [mv(M["template"], (0, 0, 450))], "setting template onto the rim",
       "Lower it over every pipe and sheath end; clamp it to the rim at four points", elev=32)
    st(8, inner + [M["template"]], [mv(M["sand"], (0, 0, 0), cut=True)], "fill with sand",
       "Pour through the template in 100 mm lifts to 571 mm, rodding each lift; weigh every bag (210 kg)", elev=32)
    filled = inner + [Q(M["sand"])]
    st(9, filled, [mv(M["head"], (0, 0, 400), cut=True)], "template off, headspace insulation in",
       "50 mm AES blanket on the sand, then stone wool to the rim, cut round every pipe", elev=30)
    st(10, filled + [Q(M["head"])], [mv(M["lid"], (0, 0, 500))], "lid and closing ring",
       "0° marks lined up; lower over all 24 pipes; rope collar round each; ring bolted", elev=30)
    lidd = filled + [Q(M["head"]), M["lid"]]
    st(11, lidd, [mv(M["collector"], (0, 0, 450))], "collector and outlet onto the lid",
       "Over the six short legs; tabs riveted to the lid with steel rivets; AES rope round the foot", elev=30)
    st(12, lidd + [M["collector"]], [mv(M["heaters"], (0, 0, 900), cut=True)], "heaters into the wells",
       "Remove the tape; lower each heater on its leads to the cap; lay the leads toward the junction box", elev=30)
    core = base + [M["drum"], M["wells"], M["utubes"], M["tc"], M["lid"], M["collector"]]
    st(13, core, [mv(M["side"], (-800 * cos(radians(32)), -800 * sin(radians(32)), 0), cut=True)], "side insulation",
       "Two 25 mm AES blanket layers, then three 89 mm stone wool batt layers, joints staggered", elev=20)
    st(14, core + [Q(M["side"])], [mv(M["jacket"], (0, 0, 1500))], "jacket side",
       "Three rows of flashing wrapped round the insulation, strapped tight, laps riveted", elev=20)
    shell = core + [M["side"], M["jacket"]]
    st(15, shell, [mv(M["top"], (0, 0, 500))], "top insulation",
       "50 mm AES over the lid and collector, then stone wool to the jacket top; heater leads and sheaths through it", elev=30)
    st(16, shell + [M["top"]], [mv(M["cap"], (0, 0, 500))], "jacket cap",
       "Over the inlet legs and outlet; leads and sheaths through their grommets; eight screws in the skirt", elev=30)
    capd = shell + [M["top"], M["cap"]]
    st(17, capd, [mv(M["trim"], (0, 0, 350))], "outlet packing and trim ring",
       "Pack the 39 mm gap with AES blanket, lay the black steel ring over it, four screws", elev=35)
    st(18, capd + [M["trim"]], [mv(M["plenum"], (0, 0, 400))], "inlet plenum",
       "Over the six inlet legs; flanges riveted to the cap and sealed with foil tape; collar at 0°", elev=30)
    st(19, capd + [M["trim"], M["plenum"]], [mv(M["jbox"], (0, 0, 350))], "heater junction box",
       "Seen from behind. Leads through the grommet into the box; land them on the ceramic terminal blocks; four screws",
       elev=30, azim=125)
    unit = capd + [M["trim"], M["plenum"], M["jbox"]]
    a = radians(35)
    st(20, unit, [mv(part("Inlet damper and servo", AIR["damper"], COL["damper"]), (300, 0, 0)),
                  mv(part("Hot outlet heat trap (guarded)", AIR["hot"], COL["duct"]), (0, 0, 300)),
                  mv(part("Mixing tee and balancing damper", AIR["tee"], "#64748B"), (300 * cos(a), 300 * sin(a), 0)),
                  mv(part("Inline fan, then duct to the room", AIR["fan"], COL["fan"]), (300 * cos(a), 300 * sin(a), -150))],
       "air path: damper, outlet duct, tee and fan",
       "Damper on the inlet collar; outlet rises and turns down to the tee; fan below the tee, then flexible duct", elev=18)
    return out


# ----------------------------------------------------------------- warning label positions (step 22)
def label_positions():
    """Where the five warning labels go (BOM line 47). Panels 1 to 3 are drawn from model.py; panels 4 and 5
    follow the air path and enclosure layout of the appearance model (not part of model.py)."""
    from matplotlib.patches import Rectangle, Circle
    from matplotlib.transforms import Affine2D
    fig, plt = _fig(14, 6.4, "Step 22: warning labels, five in all",
                    "Stick each label to clean, dry metal after the unit is finished. Positions are to scale within each panel (mm)")
    WARN = "#F59E0B"
    ro, zt = D["jacket_r_o"], D["jacket_top_z"]
    ang, zl, lw_, lh_ = P["label_jacket"]
    # 1 jacket side
    ax = fig.add_axes([0.03, 0.14, 0.17, 0.70]); ax.set_aspect("equal"); ax.axis("off")
    ax.add_patch(Rectangle((-ro, 0), 2 * ro, zt, fc="#E5E7EB", ec=MUT, lw=1))
    ax.add_patch(Rectangle((-ro, zt - P["cap_skirt"]), 2 * ro, P["cap_skirt"], fc="#CBD5E1", ec=MUT, lw=1))
    ax.add_patch(Rectangle((-lw_ / 2, zl - lh_ / 2), lw_, lh_, fc=WARN, ec=INK, lw=1.2))
    ax.annotate("HOT SURFACES\nINSIDE", (lw_ / 2, zl), (ro * 0.2, zl - 330), fontsize=7.5, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.8), ha="left")
    ax.set_xlim(-ro - 20, ro + 20); ax.set_ylim(-20, zt + 120)
    ax.set_title("1  Jacket side, from the front (0°)", fontsize=8.5, color=INK, loc="left")
    # 2 cap plan
    ax = fig.add_axes([0.22, 0.14, 0.27, 0.70]); ax.set_aspect("equal"); ax.axis("off")
    rc = ro + P["jacket_t"]
    ax.add_patch(Circle((0, 0), rc, fc="#E5E7EB", ec=MUT, lw=1))
    pl_ro, pl_ri = P["leg_outer_r"] + 45, P["leg_outer_r"] - 45
    ax.add_patch(Circle((0, 0), pl_ro, fc="none", ec="#0F766E", lw=1.0, ls="--"))
    ax.add_patch(Circle((0, 0), pl_ri, fc="#E5E7EB", ec="#0F766E", lw=1.0, ls="--"))
    ax.text(0, -(pl_ri + pl_ro) / 2 - 8, "inlet plenum", fontsize=6.5, color="#0F766E", ha="center")
    ax.add_patch(Circle((0, 0), P["trim_ring"][0] / 2, fc="#374151", ec=INK, lw=1))
    ax.add_patch(Circle((0, 0), P["trim_ring"][1] / 2, fc="white", ec=INK, lw=1))
    jang, jr, jx, jy, jh = P["jbox"]
    jx0, jy0 = _polar(jr, jang)
    ax.add_patch(Rectangle((-jx / 2, -jy / 2), jx, jy, fc="#DDD6FE", ec="#6D28D9", lw=1,
                           transform=Affine2D().rotate_deg(jang).translate(jx0, jy0) + ax.transData))
    ax.text(jx0, jy0 + 120, "junction box", fontsize=6.5, color="#6D28D9", ha="center")
    ang2, rl, w2, h2 = P["label_cap"]
    lx, ly = _polar(rl, ang2)
    ax.add_patch(Rectangle((-w2 / 2, -h2 / 2), w2, h2, fc=WARN, ec=INK, lw=1.2,
                           transform=Affine2D().rotate_deg(ang2 + 90).translate(lx, ly) + ax.transData))
    ax.annotate("HOT OUTLET", (lx, ly), (lx + 60, ly - 120), fontsize=7.5, color=INK, ha="center",
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
    ax.set_xlim(-rc - 10, rc + 10); ax.set_ylim(-rc - 10, rc + 10)
    ax.set_title("2  Jacket cap, from above", fontsize=8.5, color=INK, loc="left")
    # 3 junction box face
    ax = fig.add_axes([0.51, 0.34, 0.12, 0.30]); ax.set_aspect("equal"); ax.axis("off")
    bw, bh = P["label_jbox"]
    ax.add_patch(Rectangle((-jy / 2, 0), jy, jh, fc="#DDD6FE", ec="#6D28D9", lw=1))
    ax.add_patch(Rectangle((-bw / 2, jh / 2 - bh / 2), bw, bh, fc=WARN, ec=INK, lw=1.2))
    ax.text(0, jh / 2, "DANGER\n240 V", fontsize=7, color=INK, ha="center", va="center", fontweight="bold")
    ax.set_xlim(-jy / 2 - 10, jy / 2 + 10); ax.set_ylim(-10, jh + 10)
    ax.set_title("3  Junction box, outer face", fontsize=8.5, color=INK, loc="left")
    # 4 guard sleeve drop
    ax = fig.add_axes([0.66, 0.14, 0.12, 0.70]); ax.set_aspect("equal"); ax.axis("off")
    rs = P["outlet_d"] / 2 + 28
    ax.add_patch(Rectangle((-rs, 0), 2 * rs, 420, fc="#D1D5DB", ec=MUT, lw=1, hatch="..."))
    ax.add_patch(Rectangle((-rs - 3, 255), 2 * rs + 6, 60, fc=WARN, ec=INK, lw=1.2))
    ax.annotate("HOT SURFACE, on the drop,\nfacing the room", (rs + 3, 285), (rs + 25, 120), fontsize=7, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK, lw=0.8))
    ax.set_xlim(-rs - 30, rs + 260); ax.set_ylim(-20, 460)
    ax.set_title("4  Outlet guard sleeve", fontsize=8.5, color=INK, loc="left")
    # 5 enclosure door
    ax = fig.add_axes([0.81, 0.30, 0.17, 0.34]); ax.set_aspect("equal"); ax.axis("off")
    ew, eh = 300.0, 250.0
    ax.add_patch(Rectangle((-ew / 2, -eh / 2), ew, eh, fc="#E2E8F0", ec=MUT, lw=1))
    ax.add_patch(Rectangle((60 - 35, -78 - 24), 70, 48, fc=WARN, ec=INK, lw=1.2))
    ax.text(60, -78, "DANGER\n240 V", fontsize=6, color=INK, ha="center", va="center", fontweight="bold")
    ax.set_xlim(-ew / 2 - 10, ew / 2 + 10); ax.set_ylim(-eh / 2 - 10, eh / 2 + 10)
    ax.set_title("5  Control enclosure door", fontsize=8.5, color=INK, loc="left")
    fig.text(0.03, 0.075, "Vinyl labels rated 105 °C or higher. Labels 1 and 2 are 96 x 64 mm, label 3 is 90 x 44 mm, label 4 is 84 x 60 mm, "
             "label 5 is 70 x 48 mm. In panel 2 the dark ring is the outlet trim ring.", fontsize=8, color=MUT)
    out = OUT / "step-22.png"
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


# ----------------------------------------------------------------- wiring
def wiring():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig = plt.figure(figsize=(12, 7.6), dpi=150)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 120); ax.set_ylim(0, 76); ax.set_axis_off()
    ax.text(2, 74, "ThermaBrick prototype: block-level wiring and the safety chain", fontsize=13, fontweight="bold", color=INK, va="top")
    ax.text(2, 70.6, "240 V work is done or checked by a licensed electrician. Bought modules, wired at block level; no circuit board is laid out.",
            fontsize=8.5, color=MUT, va="top")
    ax.text(2, 1.5, "BUILD PLAN ILLUSTRATION, PLAN NOT YET BUILT", fontsize=7, color="#B45309")
    ax.text(118, 1.5, "github.com/BoujeeEnjinia1701/thermabrick", fontsize=7, color=AC, ha="right", family="monospace")
    ax.add_patch(FancyBboxPatch((24, 14), 66, 50, boxstyle="round,pad=0.4", fc="#F8FAFC", ec="#94A3B8", lw=1, ls="--"))
    ax.text(25.5, 62.8, "Control enclosure, steel, on the wall beside the unit", fontsize=8, color=MUT, va="top")

    def blk(x, y, w, h, title, sub, color):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3", fc="white", ec=color, lw=1.8))
        ax.text(x + w / 2, y + h - 1.3, title, ha="center", va="top", fontsize=8.6, fontweight="bold", color=INK)
        ax.text(x + w / 2, y + h - 4.1, sub, ha="center", va="top", fontsize=7, color=MUT, linespacing=1.3)

    def wire(pts, color, lw=2.0):
        xs, ys = zip(*pts)
        ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=1)

    def lab(x, y, text, color, ha="left"):
        ax.text(x, y, text, fontsize=7, color=color, ha=ha, va="center", zorder=3,
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))
    RED, BLU, GRY, ORG = "#B91C1C", "#1D4ED8", "#6B7280", "#C2410C"
    blk(2, 48, 17, 11, "Main panel", "2-pole 20 A GFCI\nbreaker, 240 V", RED)
    blk(2, 30, 17, 11, "Export meter", "CT clamps on the\ngrid conductors", BLU)
    blk(27, 48, 16, 11, "Fuses, 2 groups", "2-pole 10 A\nclass CC each", RED)
    blk(47, 48, 16, 11, "Safety contactor", "2-pole 30 A,\n24 V AC coil", RED)
    blk(67, 48, 20, 11, "SSR 1 and SSR 2", "25 A zero-cross, on\nheat sinks, 6 heaters each", RED)
    blk(27, 32, 16, 11, "Control transformer", "240 to 24 V AC,\n40 VA, fused", GRY)
    blk(47, 32, 16, 11, "High limit", "1/16 DIN, type K (T3),\n600 °C, latching", ORG)
    blk(67, 30, 20, 13, "ESP32 controller", "MAX31856 x 7 (T1, T2,\nT4 to T8), DS18B20 x 3,\n12 V and 5 V supply", AC)
    blk(27, 16, 16, 11, "12 V supply", "DIN rail, 2 A,\n5 V buck", GRY)
    blk(95, 48, 22, 11, "Junction box (unit top)", "12 heaters, 250 W each,\nceramic terminal blocks", RED)
    blk(95, 30, 22, 13, "On the unit", "thermocouples T1 to T8,\ndamper servo, fan speed,\nair and surface sensors", AC)
    wire([(19, 53.5), (27, 53.5)], RED); lab(23, 56, "12 AWG", RED, "center")
    wire([(43, 53.5), (47, 53.5)], RED)
    wire([(63, 53.5), (67, 53.5)], RED)
    wire([(87, 53.5), (95, 53.5)], RED); lab(91, 56, "14 AWG high-temp", RED, "center")
    wire([(35, 48), (35, 43)], GRY, 1.2)
    wire([(43, 37.5), (47, 37.5)], ORG, 1.4); lab(45, 40, "coil", ORG, "center")
    wire([(55, 43), (55, 48)], ORG, 1.4); lab(55.6, 45.5, "limit opens the coil", ORG)
    wire([(19, 35.5), (24, 35.5), (24, 28), (67, 28), (67, 33)], BLU, 1.2); lab(40, 26.5, "meter signal, Wi-Fi local API", BLU, "center")
    wire([(87, 36.5), (95, 36.5)], BLU, 1.2); lab(91, 39, "TC extension", BLU, "center")
    wire([(77, 43), (77, 48)], GRY, 1.2); lab(77.6, 45.5, "SSR control", GRY)
    wire([(43, 21.5), (77, 21.5), (77, 30)], GRY, 1.2); lab(60, 19.8, "12 V", GRY, "center")
    wire([(117, 48), (117, 43)], ORG, 1.2); lab(116.5, 45.5, "T3 to high limit", ORG, "right")
    ax.text(2, 10.5, "Safety chain: the high limit (T3 at 600 °C) opens the 24 V coil, and the contactor opens both "
            "legs of both heater groups. It latches until reset by hand.", fontsize=7.6, color="#B45309", fontweight="bold")
    ax.text(2, 7.2, "Red: 240 V power. Blue: signal. Orange: safety chain. Grey: low voltage control. Heater leads to the junction box are the "
            "heaters' own 72 in ceramic-beaded leads.", fontsize=7.2, color=MUT)
    out = OUT / "wiring.png"
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, facecolor="white"); plt.close(fig)
    return out


if __name__ == "__main__":
    what = sys.argv[1:] or ["overview", "sheets", "layouts", "joints", "steps", "wiring", "labels"]
    fns = {"overview": overview, "sheets": sheets, "layouts": layouts, "joints": joints, "steps": steps, "wiring": wiring, "labels": label_positions}
    for w in what:
        if w.startswith("steps:"):
            r = steps([int(n) for n in w[6:].split(",")])
        else:
            r = fns[w]()
        print(w, "->", r)
