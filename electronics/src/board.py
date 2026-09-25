#!/usr/bin/env python3
"""ThermaBrick controller board: schematic, PCB layout and fabrication files (TBK-DWG-004).

Run from the repo root:  python electronics/src/board.py

Stage 1 (any Python 3.9+): writes the board schematic and project library to
electronics/controller-board/, runs ERC and checks every net (reusing schematic.py).
Stage 2 (KiCad's bundled Python, started automatically): places the footprints,
routes the board with a two-layer grid router, pours GND, runs DRC with schematic
parity, and exports gerbers, drill files and the TBK-DWG-004 sheet.

The board carries the low-voltage controller only: ESP32-DevKitC V4, five MAX6675
modules, a 12 V to 5 V regulator, the SSR driver and the blower driver. Mains wiring
(fuse, latching relay, SSR, REX-C100, heaters) stays as panel wiring per TBK-DWG-003.
Licensed MIT (the script) and CERN-OHL-S-2.0 (the design it produces).
"""
import json
import math
import heapq
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import schematic as S  # noqa: E402

NAME = "thermabrick-controller-board"
OUT = ROOT / "electronics" / "controller-board"
DWG, REV, DATE = "TBK-DWG-004", "P1", "2026-09-24"
G = S.G
P_IN, P_OUT, PASS, TRI, IN, DOUT = S.P_IN, S.P_OUT, S.PASS, S.TRI, S.IN, S.DOUT

# ---------------------------------------------------------------- ESP32-DevKitC V4 pinout
# Espressif ESP32-DevKitC V4 user guide: header J2 (left, pads 1-19) and J3 (right, pads 20-38),
# both numbered from the antenna end. Rows are 25.4 mm apart.
J2 = ["3V3", "EN", "VP", "VN", "IO34", "IO35", "IO32", "IO33", "IO25", "IO26", "IO27", "IO14", "IO12",
      "GND", "IO13", "D2", "D3", "CMD", "5V"]
J3 = ["GND", "IO23", "IO22", "TX", "RX", "IO21", "GND", "IO19", "IO18", "IO5", "IO17", "IO16", "IO4",
      "IO0", "IO2", "IO15", "D1", "D0", "CLK"]
DEVKIT_PAD = {}
for i, n in enumerate(J2):
    DEVKIT_PAD.setdefault(n, []).append(str(i + 1))
for i, n in enumerate(J3):
    DEVKIT_PAD.setdefault(n, []).append(str(i + 20))
USED = {"3V3": "+3V3", "5V": "+5V", "GND": "GND", "IO18": "SCK", "IO19": "SO", "IO5": "CS_T1", "IO17": "CS_T3",
        "IO16": "CS_T4", "IO4": "CS_T5", "IO22": "CS_T6", "IO26": "SSR_IN", "IO25": "BLOWER_PWM"}


def pin_type(name):
    return {"3V3": P_OUT, "5V": P_IN, "GND": P_IN, "IO19": IN}.get(name, DOUT if name in USED else PASS)


devkit_left = [(str(i + 1), n, pin_type(n)) for i, n in enumerate(J2)]
devkit_right = [(str(i + 20), n, pin_type(n)) for i, n in enumerate(J3)]
devkit_nets = {}
for n, pads in DEVKIT_PAD.items():
    for p in pads:
        devkit_nets[p] = USED.get(n)

CUSTOM = {
    "Term2": S.box_symbol("Term2", "J", "Screw terminal 1x2 5.08 mm", [("1", "1", PASS), ("2", "2", PASS)], [],
                          7.62, "2-way 5.08 mm screw terminal"),
    "R78E": S.box_symbol("R78E", "U", "R-78E5.0-1.0", [("1", "VIN", P_IN), ("2", "GND", P_IN)],
                         [("3", "VOUT", P_OUT)], 12.7, "RECOM R-78E switching regulator, SIP-3"),
    "DevKitC": S.box_symbol("DevKitC", "U", "ESP32-DevKitC V4", devkit_left, devkit_right, 20.32,
                            "ESP32-DevKitC V4 in two 1x19 sockets, rows 25.4 mm apart"),
    "MAX6675_Socket": S.box_symbol("MAX6675_Socket", "U", "MAX6675 module",
                                   [], [("1", "GND", P_IN), ("2", "VCC", P_IN), ("3", "SCK", IN), ("4", "CS", IN),
                                        ("5", "SO", TRI)], 12.7, "MAX6675 module on a 1x5 socket (GND VCC SCK CS SO)"),
}
STD = [("Device", "R"), ("Device", "C_Polarized"), ("Device", "D"), ("Transistor_BJT", "Q_NPN_EBC"),
       ("Transistor_FET", "Q_NMOS_GDS"), ("power", "GND"), ("power", "+3V3"), ("power", "+5V"),
       ("power", "+12V"), ("power", "PWR_FLAG")]

FP_R = "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal"
FP_TERM = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal"
FP_CP = "Capacitor_THT:CP_Radial_D5.0mm_P2.00mm"
FOOTPRINTS_STD = {
    "J1": FP_TERM, "J2": FP_TERM, "J3": FP_TERM, "C1": FP_CP, "C2": FP_CP,
    "U1": "Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT",
    "R1": FP_R, "R2": FP_R, "R3": FP_R, "R4": FP_R,
    "Q1": "Package_TO_SOT_THT:TO-92_Inline_Wide", "Q2": "Package_TO_SOT_THT:TO-220-3_Vertical",
    "D1": "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal",
}
# Every footprint is copied into the project library TB, so the project needs no global libraries
FOOTPRINTS = {ref: "TB:" + fp.split(":", 1)[1] for ref, fp in FOOTPRINTS_STD.items()}
FOOTPRINTS["U2"] = "TB:ESP32_DevKitC_V4_Socket"
TCS = [("U3", "CS_T1", "T1 well wall"), ("U4", "CS_T3", "T3 sand center"), ("U5", "CS_T4", "T4 sand outer"),
       ("U6", "CS_T5", "T5 outlet air"), ("U7", "CS_T6", "T6 room air")]
for u, _cs, _l in TCS:
    FOOTPRINTS[u] = "TB:MAX6675_Module_Socket"
MOUNTING_HOLE = "MountingHole:MountingHole_3.2mm_M3"

PARTS = [
    ("J1", "TB:Term2", "12 V in", 30.48, 40.64, {"1": "+12V", "2": "GND"}),
    ("#FLG01", "TB:PWR_FLAG", "PWR_FLAG", 30.48, 58.42, {"1": "+12V"}),
    ("#FLG02", "TB:PWR_FLAG", "PWR_FLAG", 43.18, 58.42, {"1": "GND"}),
    ("C1", "TB:C_Polarized", "10u 25V", 60.96, 40.64, {"1": "+12V", "2": "GND"}),
    ("U1", "TB:R78E", "R-78E5.0-1.0", 91.44, 40.64, {"1": "+12V", "2": "GND", "3": "+5V"}),
    ("C2", "TB:C_Polarized", "22u 10V", 121.92, 40.64, {"1": "+5V", "2": "GND"}),
    ("U2", "TB:DevKitC", "ESP32-DevKitC V4", 190.5, 104.14, devkit_nets),
    ("R1", "TB:R", "10k", 33.02, 101.6, {"1": "SSR_IN", "2": "GND"}),
    ("R3", "TB:R", "1k", 50.8, 101.6, {"1": "SSR_IN", "2": "Q1_B"}),
    ("Q1", "TB:Q_NPN_EBC", "2N3904", 71.12, 101.6, {"1": "GND", "2": "Q1_B", "3": "SSR_DRV"}),
    ("J2", "TB:Term2", "SSR drive", 99.06, 101.6, {"1": "+5V", "2": "SSR_DRV"}),
    ("R2", "TB:R", "10k", 33.02, 144.78, {"1": "BLOWER_PWM", "2": "GND"}),
    ("R4", "TB:R", "100", 50.8, 144.78, {"1": "BLOWER_PWM", "2": "Q2_G"}),
    ("Q2", "TB:Q_NMOS_GDS", "IRLZ44N", 71.12, 144.78, {"1": "Q2_G", "2": "BLOWER_N", "3": "GND"}),
    ("D1", "TB:D", "1N5819", 88.9, 144.78, {"1": "+12V", "2": "BLOWER_N"}),
    ("J3", "TB:Term2", "Blower", 111.76, 144.78, {"1": "+12V", "2": "BLOWER_N"}),
]
for i, (u, cs, label) in enumerate(TCS):
    PARTS.append((u, "TB:MAX6675_Socket", f"MAX6675 module, {label}", 279.4, 45.72 + i * 22.86,
                  {"1": "GND", "2": "+3V3", "3": "SCK", "4": cs, "5": "SO"}))

NOTES = [
    (20.32, 25.4, "THERMABRICK CONTROLLER BOARD (low voltage). Mains wiring stays on the panel per TBK-DWG-003.", 1.5),
    (20.32, 83.82, "SSR DRIVE: GPIO26 high turns Q1 on; J2 feeds the SSR input (+5V to SSR 3, Q1 collector to SSR 4).", 1.27),
    (20.32, 127.0, "BLOWER DRIVE: GPIO25 PWM on Q2 (logic-level MOSFET); D1 clamps the blower's inductive kick.", 1.27),
    (20.32, 180.34, "1. R1 and R2 hold Q1 and Q2 off while the ESP32 boots or resets (TBK-TST-001, section 1, item 5).", 1.27),
    (20.32, 184.15, "2. U2 is an ESP32-DevKitC V4 (38 pins, rows 25.4 mm apart). 30-pin and narrow clones do not fit.", 1.27),
    (20.32, 187.96, "3. U3 to U7: MAX6675 modules with pins GND VCC SCK CS SO; thermocouples land on the modules.", 1.27),
    (20.32, 191.77, "4. Firmware pins and fault logic: firmware/README.md. Same nets as TBK-DWG-003 low-voltage section.", 1.27),
]

CIRCUIT = {
    "name": NAME, "out": OUT, "parts": PARTS, "notes": NOTES, "footprints": FOOTPRINTS,
    "title": "ThermaBrick controller board",
    "comment": f"{DWG} schematic. Generated by electronics/src/board.py; do not edit by hand.",
    "custom": CUSTOM, "std": STD, "rev": REV,
}


# ---------------------------------------------------------------- custom footprints
def fp_header(name, descr):
    return [f'(footprint "{name}"', '  (version 20240108)', '  (generator "thermabrick_board_py")',
            '  (layer "F.Cu")', f'  (descr "{descr}")', '  (attr through_hole)']


def fp_text(kind, text, x, y, layer, size=1.0, hide=False):
    h = "\n    (hide yes)" if hide else ""
    return (f'  (property "{kind}" "{text}" (at {x} {y} 0) (layer "{layer}"){h}\n'
            f'    (effects (font (size {size} {size}) (thickness 0.15))))')


def fp_rect(x1, y1, x2, y2, layer, w=0.12):
    return (f'  (fp_rect (start {x1} {y1}) (end {x2} {y2}) (stroke (width {w}) (type solid)) (fill no) '
            f'(layer "{layer}"))')


def fp_label(text, x, y, size=0.8, layer="F.SilkS", rot=0):
    return (f'  (fp_text user "{text}" (at {x} {y} {rot}) (layer "{layer}")\n'
            f'    (effects (font (size {size} {size}) (thickness 0.12))))')


def fp_pad(num, x, y, first=False, size=1.7, drill=1.0):
    shape = "rect" if first else "circle"
    return (f'  (pad "{num}" thru_hole {shape} (at {x} {y}) (size {size} {size}) (drill {drill}) '
            f'(layers "*.Cu" "*.Mask"))')


def write_footprints(lib_dir):
    lib_dir.mkdir(parents=True, exist_ok=True)
    # ESP32-DevKitC V4 in two 1x19 sockets. Origin at J2 pad 1; +y toward the USB end.
    L = fp_header("ESP32_DevKitC_V4_Socket", "ESP32-DevKitC V4 (38 pin) in two 1x19 2.54 mm sockets, rows 25.4 mm apart")
    L += [fp_text("Reference", "REF**", 12.7, -9.5, "F.SilkS"), fp_text("Value", "ESP32-DevKitC V4", 12.7, 22.86, "F.Fab")]
    L.append(fp_rect(-1.5, -7.5, 26.9, 48.3, "F.CrtYd", 0.05))
    L.append(fp_rect(-1.4, -7.4, 26.8, 48.2, "F.SilkS"))
    L.append(fp_rect(-1.4, -7.4, 26.8, 48.2, "F.Fab", 0.1))
    L.append(fp_label("ANTENNA", 12.7, -5.0))
    L.append(fp_label("USB", 12.7, 46.5))
    for i, n in enumerate(J2):
        L.append(fp_pad(str(i + 1), 0, round(i * 2.54, 2), first=(i == 0)))
        if n in USED:
            L.append(fp_label(n, 3.8, round(i * 2.54, 2), 0.8))
    for i, n in enumerate(J3):
        L.append(fp_pad(str(i + 20), 25.4, round(i * 2.54, 2)))
        if n in USED:
            L.append(fp_label(n, 21.6, round(i * 2.54, 2), 0.8))
    L.append(")")
    (lib_dir / "ESP32_DevKitC_V4_Socket.kicad_mod").write_text("\n".join(L) + "\n")
    # MAX6675 module standing in a 1x5 socket. Origin at pad 1 (GND); pads along +x.
    L = fp_header("MAX6675_Module_Socket", "MAX6675 thermocouple module in a 1x5 2.54 mm socket, standing upright")
    L += [fp_text("Reference", "REF**", 5.08, -3.5, "F.SilkS"), fp_text("Value", "MAX6675", 5.08, 5.0, "F.Fab")]
    L.append(fp_rect(-2.8, -2.6, 12.96, 5.4, "F.CrtYd", 0.05))
    L.append(fp_rect(-2.7, -2.5, 12.86, 5.3, "F.SilkS"))
    for i, n in enumerate(["GND", "VCC", "SCK", "CS", "SO"]):
        L.append(fp_pad(str(i + 1), round(i * 2.54, 2), 0, first=(i == 0)))
        L.append(fp_label(n, round(i * 2.54, 2), 3.3, 0.8, rot=90))
    L.append(")")
    (lib_dir / "MAX6675_Module_Socket.kicad_mod").write_text("\n".join(L) + "\n")
    # Standard footprints copied in, so the project is self-contained
    src = S.KICAD_APP / "Contents/SharedSupport/footprints"
    for fp in set(FOOTPRINTS_STD.values()) | {MOUNTING_HOLE}:
        lib, name = fp.split(":", 1)
        shutil.copy(src / f"{lib}.pretty" / f"{name}.kicad_mod", lib_dir / f"{name}.kicad_mod")


def write_tables():
    (OUT / "fp-lib-table").write_text(
        '(fp_lib_table\n  (version 7)\n  (lib (name "TB")(type "KiCad")(uri "${KIPRJMOD}/thermabrick.pretty")'
        '(options "")(descr "ThermaBrick project footprints"))\n)\n')
    pro = {
        "meta": {"filename": f"{NAME}.kicad_pro", "version": 3},
        "board": {"design_settings": {
            "defaults": {"board_outline_line_width": 0.1},
            "rules": {"min_clearance": 0.2, "min_track_width": 0.25, "min_via_diameter": 0.6,
                      "min_through_hole_diameter": 0.3, "min_hole_to_hole": 0.25, "min_copper_edge_clearance": 0.5},
            "track_widths": [0.0, 0.3, 0.8], "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.8, "drill": 0.4}]}},
        "net_settings": {"classes": [
            {"name": "Default", "clearance": 0.2, "track_width": 0.3, "via_diameter": 0.8, "via_drill": 0.4,
             "diff_pair_gap": 0.25, "diff_pair_width": 0.2, "diff_pair_via_gap": 0.25, "microvia_diameter": 0.3,
             "microvia_drill": 0.1, "wire_width": 6, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)",
             "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 2147483647},
            {"name": "Power", "clearance": 0.25, "track_width": 0.8, "via_diameter": 1.0, "via_drill": 0.5,
             "diff_pair_gap": 0.25, "diff_pair_width": 0.2, "diff_pair_via_gap": 0.25, "microvia_diameter": 0.3,
             "microvia_drill": 0.1, "wire_width": 6, "bus_width": 12, "line_style": 0, "schematic_color": "rgba(0, 0, 0, 0.000)",
             "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": 0}],
            "net_colors": None, "netclass_assignments": None,
            "netclass_patterns": [{"netclass": "Power", "pattern": n} for n in ("+12V", "+5V", "GND", "*BLOWER_N")]},
        "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
        "sheets": [], "boards": [], "text_variables": {},
    }
    (OUT / f"{NAME}.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n")


def stage1():
    sch, lib = S.build(CIRCUIT)
    S.write_project(sch, lib, CIRCUIT)
    write_tables()
    write_footprints(OUT / "thermabrick.pretty")
    print(f"wrote {OUT.relative_to(ROOT)}/{NAME}.kicad_sch ({len(PARTS)} parts, {len(S.expected_nets(CIRCUIT))} nets)")
    ok = S.check_and_export(CIRCUIT, keep_netlist=True, svg=False)
    if not ok:
        sys.exit("schematic checks failed")


# ================================================================ stage 2: PCB (KiCad Python)
BOARD = (100.0, 100.0, 210.0, 180.0)        # x1, y1, x2, y2 in mm
PLACE = {                                   # ref: (x, y, rotation deg)
    "U2": (111.76, 129.54, 0),
    "U1": (168.91, 124.46, 0), "C1": (157.48, 124.46, 0), "C2": (180.34, 124.46, 0),
    "J1": (201.93, 124.46, 90),
    "R1": (151.13, 140.97, 0), "R3": (151.13, 147.32, 0), "Q1": (170.18, 144.78, 0),
    "J2": (201.93, 142.24, 90),
    "R2": (151.13, 160.02, 0), "R4": (151.13, 166.37, 0), "Q2": (171.45, 163.83, 0),
    "D1": (176.53, 172.72, 0),
    "J3": (201.93, 165.1, 90),
}
for i, (u, _cs, _l) in enumerate(TCS):
    PLACE[u] = (111.76 + i * 19.05, 106.68, 0)
HOLES = [(104.0, 104.0), (206.0, 104.0), (104.0, 176.0), (206.0, 176.0)]
SILK = [
    (160.0, 173.6, "ThermaBrick controller", 1.0),
    (160.0, 175.6, "TBK-DWG-004 Rev P1", 1.0),
    (160.0, 177.5, "CERN-OHL-S-2.0", 0.8),
]
WIDTH = {"+12V": 0.8, "+5V": 0.8, "BLOWER_N": 0.8, "+3V3": 0.5}
DEFAULT_W = 0.3
CLEAR = 0.25            # router clearance, above the 0.2 mm rule for margin
GND_HALO = 0.6          # extra keep-away around GND pads for thermal spokes
GRID = 0.3175           # 1/8 of 2.54 mm


def nm(v):
    import pcbnew
    return pcbnew.FromMM(v)


def read_netlist():
    tree = S.parse((OUT / f"{NAME}.net").read_text())[0]
    comps, nets = {}, {}
    for c in S.find(S.find(tree, "components")[0], "comp"):
        ref = str(S.find(c, "ref")[0][1])
        tst = S.find(c, "tstamps")
        comps[ref] = str(tst[0][1]) if tst else None
    for n in S.find(S.find(tree, "nets")[0], "net"):
        name = str(S.find(n, "name")[0][1])          # keep KiCad's "/NAME" for label nets
        for x in S.find(n, "node"):
            ref, pin = str(S.find(x, "ref")[0][1]), str(S.find(x, "pin")[0][1])
            if not ref.startswith("#"):
                nets.setdefault(name, []).append((ref, pin))
    return comps, nets


class Router:
    """Two-layer grid router (A* with 45 degree moves). Layer 0 is F.Cu, layer 1 is B.Cu.
    B.Cu carries the GND pour, so it costs more and every layer change costs a via."""

    def __init__(self, x1, y1, x2, y2, g):
        self.g, self.x0, self.y0 = g, x1, y1
        self.nx, self.ny = int((x2 - x1) / g) + 1, int((y2 - y1) / g) + 1
        self.pads = []          # (net, cx, cy, hx, hy, round)
        self.tracks = []        # (net, x1, y1, x2, y2, width, layer)
        self.vias = []          # (net, x, y, dia)
        self.edge = 0.5         # copper to board edge

    def cell(self, x, y):
        return int(round((x - self.x0) / self.g)), int(round((y - self.y0) / self.g))

    def xy(self, i, j):
        return self.x0 + i * self.g, self.y0 + j * self.g

    def blocked_map(self, net, hw):
        """Cells unusable by `net` with half width hw, per layer, as sets."""
        blk = [set(), set()]
        g = self.g

        def mark_rect(cx, cy, hx, hy, layers, rnd):
            r = CLEAR + hw
            i1, j1 = self.cell(cx - hx - r, cy - hy - r)
            i2, j2 = self.cell(cx + hx + r, cy + hy + r)
            for i in range(i1 - 1, i2 + 2):
                for j in range(j1 - 1, j2 + 2):
                    x, y = self.xy(i, j)
                    dx, dy = max(abs(x - cx) - hx, 0), max(abs(y - cy) - hy, 0)
                    if rnd:
                        d = math.hypot(x - cx, y - cy) - hx
                        dx, dy = max(d, 0), 0
                    if math.hypot(dx, dy) < r:
                        for L in layers:
                            blk[L].add((i, j))

        for pn, cx, cy, hx, hy, rnd in self.pads:
            if pn != net:
                # GND pads keep a halo free of other nets so the pours can reach them with thermal spokes
                halo = GND_HALO if pn == "GND" else 0.0
                mark_rect(cx, cy, hx + halo, hy + halo, (0, 1), rnd)
        for tn, xa, ya, xb, yb, w, L in self.tracks:
            if tn == net:
                continue
            n = max(1, int(math.hypot(xb - xa, yb - ya) / (g / 2)))
            for k in range(n + 1):
                x, y = xa + (xb - xa) * k / n, ya + (yb - ya) * k / n
                mark_rect(x, y, w / 2, w / 2, (L,), True)
        for vn, x, y, dia in self.vias:
            if vn != net:
                mark_rect(x, y, dia / 2, dia / 2, (0, 1), True)
        # board edge
        e = self.edge + hw
        for i in range(self.nx):
            for j in range(self.ny):
                x, y = self.xy(i, j)
                if x < BOARD[0] + e or x > BOARD[2] - e or y < BOARD[1] + e or y > BOARD[3] - e:
                    blk[0].add((i, j))
                    blk[1].add((i, j))
        for hx_, hy_ in HOLES:
            mark_rect(hx_, hy_, 3.2, 3.2, (0, 1), True)
        return blk

    def route(self, net, sources, target, hw, via_r, bottom_cost=4.0, via_cost=12.0):
        """A* from a set of (i, j, L) source nodes to the target pad cell (either layer).
        A layer change is allowed only where a whole via of radius via_r clears everything."""
        blk = self.blocked_map(net, hw)
        vblk = self.blocked_map(net, via_r)
        no_via = vblk[0] | vblk[1]
        ti, tj = target
        moves = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
                 (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
        openq, came, cost = [], {}, {}
        for s in sources:
            cost[s] = 0.0
            heapq.heappush(openq, (math.hypot(s[0] - ti, s[1] - tj), s))
        while openq:
            _, cur = heapq.heappop(openq)
            i, j, L = cur
            if (i, j) == (ti, tj):
                path = [cur]
                while path[-1] in came:
                    path.append(came[path[-1]])
                return path[::-1]
            c0 = cost[cur]
            nbrs = []
            for di, dj, d in moves:
                ni, nj = i + di, j + dj
                if not (0 <= ni < self.nx and 0 <= nj < self.ny):
                    continue
                if (ni, nj) in blk[L] and (ni, nj) != (ti, tj):
                    continue
                if di and dj and ((i + di, j) in blk[L] or (i, j + dj) in blk[L]):
                    continue
                nbrs.append(((ni, nj, L), d * (bottom_cost if L else 1.0)))
            if (i, j) not in blk[1 - L] and (i, j) not in no_via:
                nbrs.append(((i, j, 1 - L), via_cost))
            for nxt, step in nbrs:
                # small penalty for turning keeps traces straight
                prev = came.get(cur)
                if prev and nxt[2] == L and (nxt[0] - i, nxt[1] - j) != (i - prev[0], j - prev[1]):
                    step += 0.3
                nc = c0 + step
                if nc < cost.get(nxt, 1e18):
                    cost[nxt] = nc
                    came[nxt] = cur
                    heapq.heappush(openq, (nc + math.hypot(nxt[0] - ti, nxt[1] - tj), nxt))
        return None

    def commit(self, net, path, w, via_dia):
        """Turn a cell path into merged track segments and vias."""
        segs = []
        start = path[0]
        prev_dir = None
        for a, b in zip(path, path[1:]):
            if a[2] != b[2]:
                self._seg(net, start, a, w, segs)
                x, y = self.xy(a[0], a[1])
                self.vias.append((net, x, y, via_dia))
                start, prev_dir = b, None
                continue
            d = (b[0] - a[0], b[1] - a[1])
            if prev_dir is not None and d != prev_dir:
                self._seg(net, start, a, w, segs)
                start = a
            prev_dir = d
        self._seg(net, start, path[-1], w, segs)
        return segs

    def _seg(self, net, a, b, w, segs):
        if (a[0], a[1]) == (b[0], b[1]):
            return
        xa, ya = self.xy(a[0], a[1])
        xb, yb = self.xy(b[0], b[1])
        self.tracks.append((net, xa, ya, xb, yb, w, a[2]))
        segs.append((xa, ya, xb, yb, w, a[2]))


def stage2():
    import pcbnew
    comps, nets = read_netlist()
    board = pcbnew.BOARD()
    lib_dir = str(OUT / "thermabrick.pretty")
    board_file = OUT / f"{NAME}.kicad_pcb"

    # Outline
    x1, y1, x2, y2 = BOARD
    rect = pcbnew.PCB_SHAPE(board)
    rect.SetShape(pcbnew.SHAPE_T_RECT)
    rect.SetStart(pcbnew.VECTOR2I(nm(x1), nm(y1)))
    rect.SetEnd(pcbnew.VECTOR2I(nm(x2), nm(y2)))
    rect.SetLayer(pcbnew.Edge_Cuts)
    rect.SetWidth(nm(0.1))
    board.Add(rect)

    # Nets
    netinfo = {}
    for name in sorted(nets):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni
    pad_net = {(r, p): n for n, members in nets.items() for r, p in members}

    # Footprints
    values = {ref: val for ref, _l, val, _x, _y, _n in PARTS}
    fps = {}
    for ref, (x, y, rot) in PLACE.items():
        lib_name = FOOTPRINTS[ref].split(":", 1)[1]
        fp = pcbnew.FootprintLoad(lib_dir, lib_name)
        fp.SetFPID(pcbnew.LIB_ID("TB", lib_name))
        fp.SetReference(ref)
        fp.SetValue(values[ref])
        fp.SetPosition(pcbnew.VECTOR2I(nm(x), nm(y)))
        fp.SetOrientationDegrees(rot)
        if comps.get(ref):
            fp.SetPath(pcbnew.KIID_PATH(f"/{comps[ref]}"))
        board.Add(fp)
        for pad in fp.Pads():
            n = pad_net.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(netinfo[n])
        fps[ref] = fp
    for k, (x, y) in enumerate(HOLES):
        fp = pcbnew.FootprintLoad(lib_dir, MOUNTING_HOLE.split(":", 1)[1])
        fp.SetFPID(pcbnew.LIB_ID("TB", MOUNTING_HOLE.split(":", 1)[1]))
        fp.SetReference(f"H{k + 1}")
        fp.SetPosition(pcbnew.VECTOR2I(nm(x), nm(y)))
        fp.SetBoardOnly(True)
        fp.SetExcludedFromBOM(True)
        fp.SetExcludedFromPosFiles(True)
        fp.Reference().SetVisible(False)
        fp.Value().SetVisible(False)
        board.Add(fp)

    # Silkscreen labels: thermocouple channel under each module, terminal legends
    def silk(x, y, text, size=1.0, layer=pcbnew.F_SilkS, rot=0):
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetPosition(pcbnew.VECTOR2I(nm(x), nm(y)))
        t.SetTextAngleDegrees(rot)
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I(nm(size), nm(size)))
        t.SetTextThickness(nm(size * 0.15))
        board.Add(t)
    for u, _cs, label in TCS:
        x, y, _ = PLACE[u]
        silk(x + 5.08, y + 7.0, label, 0.9)
    for ref, legend in (("J1", "+12V  GND"), ("J2", "SSR+  SSR-"), ("J3", "FAN+  FAN-")):
        bb = fps[ref].GetBoundingBox(False)
        cy = pcbnew.ToMM(bb.GetCenter().y)
        silk(pcbnew.ToMM(bb.GetLeft()) - 2.8, cy, legend, 0.9, rot=90)
    for x, y, text, size in SILK:
        silk(x, y, text, size)

    # Router input: pad geometry
    r = Router(x1, y1, x2, y2, GRID)
    for fp in fps.values():
        for pad in fp.Pads():
            c = pad.GetPosition()
            bb = pad.GetBoundingBox()
            hx, hy = pcbnew.ToMM(bb.GetWidth()) / 2, pcbnew.ToMM(bb.GetHeight()) / 2
            rnd = pad.GetShape() == pcbnew.PAD_SHAPE_CIRCLE
            r.pads.append((pad.GetNetname() or None, pcbnew.ToMM(c.x), pcbnew.ToMM(c.y), hx, hy, rnd))

    # Route every net except GND (poured). Short, dense nets first; power last with its wide traces
    bare = lambda n: n.lstrip("/")  # noqa: E731
    order = sorted((n for n in nets if n != "GND" and len(nets[n]) > 1),   # skip unused-pin nets
                   key=lambda n: (bare(n) in WIDTH, len(nets[n])))
    failed = []
    for net in order:
        w = WIDTH.get(bare(net), DEFAULT_W)
        via = 1.0 if w > 0.5 else 0.8
        members = [(ref, pin) for ref, pin in nets[net]]
        pts = []
        for ref, pin in members:
            for pad in fps[ref].Pads():
                if pad.GetNumber() == pin:
                    c = pad.GetPosition()
                    pts.append(r.cell(pcbnew.ToMM(c.x), pcbnew.ToMM(c.y)))
        # grow a tree: connect the nearest unconnected pad each time
        tree = {(pts[0][0], pts[0][1], 0), (pts[0][0], pts[0][1], 1)}
        todo = pts[1:]
        while todo:
            todo.sort(key=lambda p: min(math.hypot(p[0] - t[0], p[1] - t[1]) for t in tree))
            tgt = todo.pop(0)
            path = r.route(net, tree, tgt, w / 2, via / 2)
            if not path:
                failed.append((net, tgt))
                continue
            r.commit(net, path, w, via)
            tree |= set(path)
            tree |= {(tgt[0], tgt[1], 0), (tgt[0], tgt[1], 1)}
        print(f"  routed {net:11s} {len(members)} pads, width {w} mm")
    if failed:
        print(f"  UNROUTED: {failed}")

    for net, xa, ya, xb, yb, w, L in r.tracks:
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(nm(xa), nm(ya)))
        t.SetEnd(pcbnew.VECTOR2I(nm(xb), nm(yb)))
        t.SetWidth(nm(w))
        t.SetLayer(pcbnew.F_Cu if L == 0 else pcbnew.B_Cu)
        t.SetNet(netinfo[net])
        board.Add(t)
    for net, x, y, dia in r.vias:
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(nm(x), nm(y)))
        v.SetWidth(nm(dia))
        v.SetDrill(nm(dia / 2))
        v.SetNet(netinfo[net])
        board.Add(v)

    # GND plane: pour on B.Cu (routing prefers F.Cu, so the plane stays nearly whole)
    for layer in (pcbnew.B_Cu,):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(netinfo["GND"])
        z.SetLocalClearance(nm(0.3))
        z.SetMinThickness(nm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline()
        ol.NewOutline()
        for px, py in ((x1 + 0.5, y1 + 0.5), (x2 - 0.5, y1 + 0.5), (x2 - 0.5, y2 - 0.5), (x1 + 0.5, y2 - 0.5)):
            ol.Append(nm(px), nm(py))
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())
    board.Save(str(board_file))
    print(f"wrote {board_file.relative_to(ROOT)}: {len(r.tracks)} segments, {len(r.vias)} vias")
    return 0 if not failed else 2


# ---------------------------------------------------------------- stage 3: checks and exports
def stage3():
    cli = S.kicad_cli()
    pcb = OUT / f"{NAME}.kicad_pcb"
    rep = OUT / "drc.json"
    subprocess.run([cli, "pcb", "drc", "--format", "json", "--severity-all", "--schematic-parity", "--refill-zones",
                    "--save-board", "-o", str(rep), str(pcb)], capture_output=True)
    d = json.loads(rep.read_text())
    viol = d.get("violations", []) + d.get("unconnected_items", []) + d.get("schematic_parity", [])
    errors = [v for v in viol if v.get("severity") == "error"]
    for v in sorted(viol, key=lambda v: v.get("severity") != "error"):
        where = "; ".join(i.get("description", "") for i in v.get("items", []))
        print(f"  DRC {v['severity']}: {v['type']}: {v['description']} [{where[:140]}]")
    print(f"DRC: {len(errors)} errors, {len(viol) - len(errors)} warnings "
          f"({len(d.get('unconnected_items', []))} unconnected, {len(d.get('schematic_parity', []))} parity)")
    rep.unlink()
    fab = OUT / "fab"
    if fab.exists():
        shutil.rmtree(fab)
    fab.mkdir()
    subprocess.run([cli, "pcb", "export", "gerbers", "-l", "F.Cu,B.Cu,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts",
                    "-o", str(fab) + "/", str(pcb)], check=True, capture_output=True)
    subprocess.run([cli, "pcb", "export", "drill", "-o", str(fab) + "/", str(pcb)], check=True, capture_output=True)
    zipf = OUT / f"{NAME}-gerbers-{REV}"
    shutil.make_archive(str(zipf), "zip", fab)
    shutil.rmtree(fab)
    return len(errors) == 0


def build_sheet():
    """TBK-DWG-004: board top (copper, silkscreen, outline) and bottom copper on the portfolio sheet."""
    cli = S.kicad_cli()
    pcb = OUT / f"{NAME}.kicad_pcb"
    tmp = OUT / "_svg"
    tmp.mkdir(exist_ok=True)
    views = {}
    for name, layers in (("top", "F.Cu,F.Silkscreen,Edge.Cuts"), ("bottom", "B.Cu,Edge.Cuts")):
        out = tmp / f"{name}.svg"
        args = [cli, "pcb", "export", "svg", "-l", layers, "--mode-single", "--page-size-mode", "2",
                "--exclude-drawing-sheet", "-o", str(out), str(pcb)]
        if name == "bottom":
            args.insert(-3, "--mirror")
        subprocess.run(args, check=True, capture_output=True)
        views[name] = out
    sys.path.insert(0, str(ROOT / ".kit"))
    from drawing import Sheet, M, TB_Y
    s = Sheet(project="ThermaBrick", title="Controller board layout", dwg_no=DWG, rev=REV, author="Amish Chadha",
              date=DATE, scale=None, units="mm",
              material="FR-4 1.6 mm, 2 layer, 1 oz copper, HASL. KiCad source in electronics/controller-board",
              revisions=[("P1", "First issue: controller board, 110 x 80 mm", DATE, "AC")])
    s.scale = 1.5
    s.add_svg(views["top"], M + 12, M + 24, 110 * 1.5, 80 * 1.5, scale=1.5, label="Top", sublabel="Copper and silkscreen, scale 3:2")
    s.add_svg(views["bottom"], M + 200, M + 24, 110 * 1.5, 80 * 1.5, scale=1.5, label="Bottom",
              sublabel="Copper, viewed from below, scale 3:2")
    notes = ["Board 110 x 80 mm, four M3 holes 102 x 72 mm apart. GND plane poured on the bottom layer.",
             "Plug in an ESP32-DevKitC V4 (38 pin, rows 25.4 mm) with its USB end toward the board edge.",
             "MAX6675 modules stand in the 1x5 sockets, pin 1 (GND) at the square pad.",
             "Fabrication files: electronics/controller-board/thermabrick-controller-board-gerbers-P1.zip",
             "Low-voltage controller only; mains wiring stays on the panel per TBK-DWG-003."]
    rows = "".join(f'<text x="0" y="{4 + k * 4.4}" font-family="IBM Plex Sans, Helvetica, Arial, sans-serif" '
                   f'font-size="2.4" fill="#111827">{n}</text>' for k, n in enumerate(notes))
    note_svg = tmp / "notes.svg"
    note_svg.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="200mm" height="24mm" '
                        f'viewBox="0 0 200 24">{rows}</svg>')
    s.add_svg(note_svg, M + 12, TB_Y - 30, scale=1.0)
    s.save(ROOT / "cad" / "drawings" / DWG)
    shutil.rmtree(tmp)
    print(f"wrote cad/drawings/{DWG} (SVG, PDF, PNG)")


def kicad_python():
    base = S.KICAD_APP / "Contents/Frameworks/Python.framework/Versions"
    for v in sorted(base.glob("*"), reverse=True):
        p = v / "bin" / "python3"
        if p.exists():
            return p
    return None


def main():
    if "--pcb" in sys.argv:
        sys.exit(stage2())
    stage1()
    py = kicad_python()
    if not py:
        sys.exit("KiCad Python not found: schematic written, PCB not built")
    r = subprocess.run([str(py), __file__, "--pcb"], cwd=ROOT)
    (OUT / f"{NAME}.net").unlink(missing_ok=True)
    if r.returncode not in (0, 2):
        sys.exit("PCB stage failed")
    ok = stage3()
    build_sheet()
    if not ok or r.returncode:
        sys.exit(1)


if __name__ == "__main__":
    main()
