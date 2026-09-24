#!/usr/bin/env python3
"""ThermaBrick test article controller schematic (KiCad), TBK-DWG-003.

Run from the repo root:  python electronics/src/schematic.py

Generates electronics/test-article/ as a KiCad project:
  thermabrick-test-article.kicad_sch   schematic (source of truth is this script)
  thermabrick-test-article.kicad_pro   project file
  thermabrick.kicad_sym, sym-lib-table project symbol library
then, with kicad-cli on the PATH or in /Applications/KiCad:
  runs ERC, exports the netlist and checks every net against NETS below,
  exports PDF and SVG, and builds the ANSI B sheet cad/drawings/TBK-DWG-003.

The circuit follows TBK-PRC-002, firmware/README.md and bom/bom-test-article.csv.
Licensed MIT (see LICENSE-SOFTWARE).
"""
import json
import re
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "electronics" / "test-article"
NAME = "thermabrick-test-article"
REV, DATE = "P1", "2026-09-24"
KICAD_APPS = [Path("/Applications/KiCad/KiCad.app"), Path.home() / "Applications/KiCad/KiCad.app",
              Path("/Volumes/KiCad/KiCad/KiCad.app")]   # installed, per-user, or the mounted disk image
KICAD_APP = next((a for a in KICAD_APPS if a.exists()), KICAD_APPS[0])
KICAD_SYMBOLS = KICAD_APP / "Contents/SharedSupport/symbols"
G = 2.54  # grid


_UID = [0]
_NS = uuid.UUID("6f1d9a52-3c0e-4a57-9b8e-7e4b2f1c0a33")


def uid():
    """Deterministic UUIDs, so regenerating an unchanged circuit gives an identical file."""
    _UID[0] += 1
    return str(uuid.uuid5(_NS, f"{NAME}-{_UID[0]}"))


# ---------------------------------------------------------------- s-expressions
class Q(str):
    """A quoted string atom."""


def parse(text):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for t in tokens:
        if t == "(":
            stack.append([])
        elif t == ")":
            done = stack.pop()
            stack[-1].append(done)
        elif t.startswith('"'):
            stack[-1].append(Q(t[1:-1].replace('\\"', '"').replace("\\\\", "\\")))
        else:
            stack[-1].append(t)
    return stack[0]


def dump(x, ind=0):
    if isinstance(x, list):
        if not any(isinstance(e, list) for e in x):
            return "(" + " ".join(dump(e) for e in x) + ")"
        pad = "  " * (ind + 1)
        head = [dump(e) for e in x if not isinstance(e, list)]
        body = [pad + dump(e, ind + 1) for e in x if isinstance(e, list)]
        # keep atom order: atoms first then lists (KiCad files always use this order)
        return "(" + " ".join(head) + "\n" + "\n".join(body) + "\n" + "  " * ind + ")"
    if isinstance(x, Q):
        return '"' + x.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(x, float):
        return f"{x:.4f}".rstrip("0").rstrip(".")
    return str(x)


def find(node, key):
    return [e for e in node if isinstance(e, list) and e and e[0] == key]


# ---------------------------------------------------------------- symbols
def std_symbol(lib, name):
    """Load a symbol from the KiCad standard library, renamed Lib:Name for embedding."""
    path = KICAD_SYMBOLS / f"{lib}.kicad_sym"
    tree = parse(path.read_text(encoding="utf-8"))[0]
    for s in find(tree, "symbol"):
        if s[1] == name:
            if find(s, "extends"):
                raise SystemExit(f"{lib}:{name} is a derived symbol; choose its parent")
            s = [e for e in s]
            s[1] = Q(f"TB:{name}")   # copied into the project library so the project is self-contained
            return s
    raise SystemExit(f"symbol {lib}:{name} not found in {path}")


def font(size=1.27, hide=False, justify=None):
    e = ["effects", ["font", ["size", size, size]]]
    if justify:
        e.append(["justify", *justify])
    if hide:
        e.append(["hide", "yes"])
    return e


def box_symbol(name, ref, value, left, right, width=15.24, desc="", top=None, bottom=None):
    """Rectangular module symbol. left/right: [(number, name, type), ...] top to bottom,
    None for a gap. Pins are 2.54 mm long on a 2.54 mm pitch."""
    rows = max(len(left), len(right)) + 1       # a blank bottom row keeps power symbols clear of the value
    h = (rows + 1) * G
    y0 = h / 2 - G
    pins = []

    def pin(num, pname, ptype, x, y, ang):
        pins.append(["pin", ptype, "line", ["at", x, y, ang], ["length", G],
                     ["name", Q(pname), font()], ["number", Q(num), font()]])

    for i, p in enumerate(left):
        if p:
            pin(p[0], p[1], p[2], -width / 2 - G, round(y0 - i * G, 2), 0)
    for i, p in enumerate(right):
        if p:
            pin(p[0], p[1], p[2], width / 2 + G, round(y0 - i * G, 2), 180)
    body = ["symbol", Q(f"{name}_0_1"),
            ["rectangle", ["start", -width / 2, h / 2], ["end", width / 2, -h / 2],
             ["stroke", ["width", 0.254], ["type", "default"]], ["fill", ["type", "background"]]]]
    return ["symbol", Q(f"TB:{name}"), ["pin_numbers", ["hide", "yes"]], ["pin_names", ["offset", 1.016]],
            ["exclude_from_sim", "no"], ["in_bom", "yes"], ["on_board", "yes"],
            ["property", Q("Reference"), Q(ref), ["at", -width / 2, h / 2 + 1.27, 0], font(justify=["left"])],
            ["property", Q("Value"), Q(value), ["at", -width / 2, -h / 2 - 1.27, 0], font(justify=["left"])],
            ["property", Q("Footprint"), Q(""), ["at", 0, 0, 0], font(hide=True)],
            ["property", Q("Datasheet"), Q(""), ["at", 0, 0, 0], font(hide=True)],
            ["property", Q("Description"), Q(desc), ["at", 0, 0, 0], font(hide=True)],
            body, ["symbol", Q(f"{name}_1_1"), *pins]]


P_IN, P_OUT, PASS, TRI, IN, DOUT = "power_in", "power_out", "passive", "tri_state", "input", "output"

CUSTOM = {
    "Mains_Plug": box_symbol("Mains_Plug", "J", "NEMA 5-15P cord, 14/3 SJT",
                             [None, ("PE", "PE", PASS)], [("L", "L", PASS), ("N", "N", PASS)], 10.16,
                             "120 V supply cord to a GFCI-protected receptacle"),
    "Relay_DPDT": box_symbol("Relay_DPDT", "K", "30 A DPDT, 120 VAC coil",
                             [("A1", "A1", PASS), ("A2", "A2", PASS), None, None],
                             [("11", "11 COM", PASS), ("14", "14 NO", PASS), ("12", "12 NC", PASS),
                              ("21", "21 COM", PASS), ("24", "24 NO", PASS), ("22", "22 NC", PASS)], 15.24,
                             "Latching power relay: pole 1 heaters, pole 2 holding contact"),
    "SSR": box_symbol("SSR", "U", "SSR-25DA zero-cross",
                      [("3", "3 +", IN), ("4", "4 -", PASS)], [("1", "1 LOAD", PASS), ("2", "2 LOAD", PASS)],
                      15.24, "Solid state relay, 3 to 32 VDC in, 24 to 380 VAC load"),
    "REX_C100": box_symbol("REX_C100", "U", "REX-C100, relay out, K input",
                           [("L", "L", PASS), ("N", "N", PASS), None, ("TC+", "TC+", PASS), ("TC-", "TC-", PASS)],
                           [("COM", "OUT COM", PASS), ("NO", "OUT NO", PASS)], 20.32,
                           "Independent high limit: relay closed while T2 < 600 C"),
    "PSU_12V": box_symbol("PSU_12V", "PS", "12 V 5 A",
                          [("L", "L", PASS), None, ("N", "N", PASS)], [("V+", "+V", P_OUT), None, ("V-", "-V", P_OUT)],
                          15.24, "AC to 12 VDC power supply"),
    "Buck": box_symbol("Buck", "U", "Buck 12 V to 5 V, 3 A",
                       [("IN+", "IN+", P_IN), None, ("IN-", "IN-", P_IN)],
                       [("OUT+", "OUT+", P_OUT), None, ("OUT-", "OUT-", PASS)],
                       15.24, "DC-DC buck converter module"),
    "MOSFET_Module": box_symbol("MOSFET_Module", "U", "Logic-level MOSFET PWM module",
                                [("VIN+", "VIN+", P_IN), None, ("PWM", "PWM", IN), None, ("VIN-", "VIN-", P_IN), None,
                                 ("GND", "GND", P_IN)],
                                [("OUT+", "OUT+", PASS), ("OUT-", "OUT-", PASS)], 17.78,
                                "Low-side MOSFET switch module for the blower"),
    "ESP32_DevKit": box_symbol("ESP32_DevKit", "U", "ESP32 DevKit (ESP32-WROOM-32)",
                               [("5V", "5V", P_IN), None, ("3V3", "3V3", P_OUT), None, None, None, None, None,
                                ("GND", "GND", P_IN)],
                               [("IO18", "IO18 SCK", DOUT), ("IO19", "IO19 SO", IN), ("IO5", "IO5 CS T1", DOUT),
                                ("IO17", "IO17 CS T3", DOUT), ("IO16", "IO16 CS T4", DOUT), ("IO4", "IO4 CS T5", DOUT),
                                ("IO22", "IO22 CS T6", DOUT), ("IO26", "IO26 SSR", DOUT), ("IO25", "IO25 PWM", DOUT)],
                               22.86, "Controller; firmware in firmware/"),
    "MAX6675": box_symbol("MAX6675", "U", "MAX6675 module",
                          [("T+", "T+", PASS), ("T-", "T-", PASS)],
                          [("VCC", "VCC", P_IN), ("SCK", "SCK", IN), ("CS", "CS", IN), ("SO", "SO", TRI),
                           ("GND", "GND", P_IN)], 12.7, "Type K thermocouple converter"),
    "Thermocouple": box_symbol("Thermocouple", "TC", "Type K", [], [("+", "+", PASS), ("-", "-", PASS)], 7.62,
                               "Type K thermocouple"),
    "Heater": box_symbol("Heater", "H", "250 W 120 V", [("1", "1", PASS)], [("2", "2", PASS)], 10.16,
                         "5/8 x 18 in cartridge heater"),
    "Blower": box_symbol("Blower", "M", "12 V blower", [("+", "+", PASS), ("-", "-", PASS)], [], 10.16,
                         "12 V DC centrifugal blower"),
}

STD = [("Device", "R"), ("Device", "Fuse"), ("Switch", "SW_Push"), ("Switch", "SW_Push_Open"),
       ("power", "GND"), ("power", "+3V3"), ("power", "+5V"), ("power", "+12V"), ("power", "Earth_Protective"),
       ("power", "PWR_FLAG")]
POWER_NETS = {"GND": "TB:GND", "+3V3": "TB:+3V3", "+5V": "TB:+5V", "+12V": "TB:+12V",
              "PE": "TB:Earth_Protective"}

# ---------------------------------------------------------------- circuit
# (ref, lib_id, value, x, y, {pin number: net}); positions in mm on A3, grid-aligned
PARTS = [
    # 120 V mains: supply, heater power path
    ("J1", "TB:Mains_Plug", "NEMA 5-15P cord, 14/3 SJT", 30.48, 45.72, {"L": "L_IN", "N": "N", "PE": "PE"}),
    ("#FLG01", "TB:PWR_FLAG", "PWR_FLAG", 30.48, 71.12, {"1": "PE"}),
    ("F1", "TB:Fuse", "10 A fast", 66.04, 45.72, {"1": "L_IN", "2": "L_F"}),
    ("K1", "TB:Relay_DPDT", "30 A DPDT, 120 VAC coil", 111.76, 50.8,
     {"A1": "L_COIL", "A2": "N", "11": "L_F", "14": "L_K", "12": None, "21": "L_STOP", "24": "L_RUN", "22": None}),
    ("U1", "TB:SSR", "SSR-25DA zero-cross", 167.64, 45.72, {"3": "SSR_IN", "4": "GND", "1": "L_K", "2": "L_HEAT"}),
    ("H1", "TB:Heater", "250 W 120 V", 213.36, 30.48, {"1": "L_HEAT", "2": "N"}),
    ("H2", "TB:Heater", "250 W 120 V", 213.36, 45.72, {"1": "L_HEAT", "2": "N"}),
    ("H3", "TB:Heater", "250 W 120 V", 213.36, 60.96, {"1": "L_HEAT", "2": "N"}),
    ("H4", "TB:Heater", "250 W 120 V", 213.36, 76.2, {"1": "L_HEAT", "2": "N"}),
    # 120 V mains: latching coil circuit and independent limit
    ("SW1", "TB:SW_Push_Open", "STOP (NC)", 45.72, 93.98, {"1": "L_F", "2": "L_STOP"}),
    ("SW2", "TB:SW_Push", "START (NO)", 81.28, 93.98, {"1": "L_STOP", "2": "L_RUN"}),
    ("U2", "TB:REX_C100", "REX-C100, relay out, K input", 134.62, 96.52,
     {"L": "L_F", "N": "N", "TC+": "TC2P", "TC-": "TC2N", "COM": "L_RUN", "NO": "L_COIL"}),
    ("TC2", "TB:Thermocouple", "T2 well wall (limit)", 180.34, 101.6, {"+": "TC2P", "-": "TC2N"}),
    # Low voltage: supplies and blower
    ("PS1", "TB:PSU_12V", "12 V 5 A", 33.02, 144.78, {"L": "L_F", "N": "N", "V+": "+12V", "V-": "GND"}),
    ("U3", "TB:Buck", "Buck 12 V to 5 V, 3 A", 76.2, 144.78, {"IN+": "+12V", "IN-": "GND", "OUT+": "+5V", "OUT-": "GND"}),
    ("U4", "TB:MOSFET_Module", "Logic-level MOSFET PWM module", 76.2, 185.42,
     {"VIN+": "+12V", "VIN-": "GND", "PWM": "BLOWER_PWM", "GND": "GND", "OUT+": "BLOWER_P", "OUT-": "BLOWER_N"}),
    ("M1", "TB:Blower", "12 V blower", 127.0, 185.42, {"+": "BLOWER_P", "-": "BLOWER_N"}),
    # Controller
    ("U5", "TB:ESP32_DevKit", "ESP32 DevKit (ESP32-WROOM-32)", 180.34, 157.48,
     {"5V": "+5V", "GND": "GND", "3V3": "+3V3", "IO18": "SCK", "IO19": "SO", "IO5": "CS_T1", "IO17": "CS_T3",
      "IO16": "CS_T4", "IO4": "CS_T5", "IO22": "CS_T6", "IO26": "SSR_IN", "IO25": "BLOWER_PWM"}),
    ("R1", "TB:R", "10k", 167.64, 198.12, {"1": "SSR_IN", "2": "GND"}),
    ("R2", "TB:R", "10k", 185.42, 198.12, {"1": "BLOWER_PWM", "2": "GND"}),
]
TC_ROWS = [("U6", "TC1", "T1", "T1 well wall (control)"), ("U7", "TC3", "T3", "T3 sand center"),
           ("U8", "TC4", "T4", "T4 sand outer"), ("U9", "TC5", "T5", "T5 exchanger outlet air"),
           ("U10", "TC6", "T6", "T6 room air")]
for i, (u, tcr, tag, label) in enumerate(TC_ROWS):
    y = 88.9 + i * 25.4
    PARTS.append((u, "TB:MAX6675", "MAX6675 module", 309.88, y,
                  {"T+": f"{tcr}P", "T-": f"{tcr}N", "VCC": "+3V3", "GND": "GND", "SCK": "SCK",
                   "CS": f"CS_{tag}", "SO": "SO"}))
    PARTS.append((tcr, "TB:Thermocouple", label, 269.24, y, {"+": f"{tcr}P", "-": f"{tcr}N"}))

NOTES = [
    (20.32, 25.4, "120 V MAINS: heater power path and latching limit circuit", 1.5),
    (20.32, 127.0, "LOW VOLTAGE: 12 V, 5 V and 3.3 V. ESP32 pins per firmware/README.md", 1.5),
    (254.0, 76.2, "THERMOCOUPLES: T1, T3 to T6 on the ESP32; T2 on U2 only", 1.5),
    (254.0, 20.32, "Notes", 1.5),
    (254.0, 25.4, "1. Cord to F1 in 14 AWG; all 120 V wiring after F1 in 16 AWG minimum, rated 105 C.", 1.27),
    (254.0, 29.21, "2. Heaters run only with K1 latched: START pressed, STOP closed, U2 relay closed (T2 < 600 C).", 1.27),
    (254.0, 33.02, "3. Any trip, STOP or power loss drops K1; it stays open until START is pressed.", 1.27),
    (254.0, 36.83, "4. U2: on-off heating action, setpoint 600 C; relay closed below setpoint, open unpowered.", 1.27),
    (254.0, 40.64, "5. R1 holds the SSR off through ESP32 boot and reset. If the SSR LED is dim at 3.3 V,", 1.27),
    (254.0, 44.45, "   drive U1 from +5V through an NPN (2N3904, 1k base resistor); keep R1.", 1.27),
    (254.0, 48.26, "6. Bond to PE: drum, wells, jacket, stack, enclosure, junction box, SSR heat sink.", 1.27),
    (254.0, 52.07, "7. K1, U1 and U2 terminal numbers are functional; follow each part's wiring label.", 1.27),
    (254.0, 55.88, "8. T2 goes only to U2, never to the ESP32, so the limit stays independent.", 1.27),
]

# Expected connectivity, checked against KiCad's exported netlist
def expected_nets():
    nets = {}
    for ref, _lib, _val, _x, _y, pins in PARTS:
        for num, net in pins.items():
            if net and not ref.startswith("#"):
                nets.setdefault(net, set()).add(f"{ref}.{num}")
    return nets


# ---------------------------------------------------------------- geometry
def pins_of(sym):
    """[(number, x, y, angle)] for unit 1 and the common unit of a library symbol."""
    out = []
    for sub in find(sym, "symbol"):
        m = re.search(r"_(\d+)_(\d+)$", str(sub[1]))
        if m and m.group(1) in ("0", "1") and m.group(2) in ("0", "1"):
            for p in find(sub, "pin"):
                at = find(p, "at")[0]
                num = find(p, "number")[0][1]
                out.append((str(num), float(at[1]), float(at[2]), float(at[3]) if len(at) > 3 else 0.0))
    return out


def sch_pin(x, y, px, py):
    return round(x + px, 2), round(y - py, 2)          # library y-up, schematic y-down


def build():
    lib = {f"TB:{k}": v for k, v in CUSTOM.items()}
    for l, n in STD:
        lib[f"TB:{n}"] = std_symbol(l, n)
    root = uid()
    items = []
    pwr = [0]

    def instance(lib_id, ref, value, x, y, pin_numbers, hidden_ref=False):
        props = [["property", Q("Reference"), Q(ref), ["at", x, y - 7.62, 0], font(hide=hidden_ref)],
                 ["property", Q("Value"), Q(value), ["at", x, y + 7.62, 0], font(hide=hidden_ref and False)],
                 ["property", Q("Footprint"), Q(""), ["at", x, y, 0], font(hide=True)],
                 ["property", Q("Datasheet"), Q(""), ["at", x, y, 0], font(hide=True)]]
        sym = lib[lib_id]
        for prop in find(sym, "property"):   # place ref and value as the library does
            if prop[1] in ("Reference", "Value"):
                at = find(prop, "at")[0]
                px, py = sch_pin(x, y, float(at[1]), float(at[2]))
                ang = float(at[3]) if len(at) > 3 else 0
                for p in props:
                    if p[1] == prop[1]:
                        p[3] = ["at", px, py, ang]
                        eff = find(prop, "effects")
                        if eff and not (hidden_ref and prop[1] == "Reference"):
                            p[4] = eff[0]
        items.append(["symbol", ["lib_id", Q(lib_id)], ["at", x, y, 0], ["unit", 1],
                      ["exclude_from_sim", "no"], ["in_bom", "no" if hidden_ref else "yes"],
                      ["on_board", "yes"], ["dnp", "no"], ["uuid", Q(uid())], *props,
                      *[["pin", Q(n), ["uuid", Q(uid())]] for n in pin_numbers],
                      ["instances", ["project", Q(NAME), ["path", Q(f"/{root}"), ["reference", Q(ref)], ["unit", 1]]]]])

    def power(net, x, y, ang):
        pwr[0] += 1
        lib_id = POWER_NETS[net]
        # GND and PE hang below the stub end; supply rails sit above it
        instance(lib_id, f"#PWR{pwr[0]:03d}", net, x, y, ["1"], hidden_ref=True)

    for ref, lib_id, value, x, y, netmap in PARTS:
        sym = lib[lib_id]
        pins = pins_of(sym)
        instance(lib_id, ref, value, x, y, [p[0] for p in pins], hidden_ref=ref.startswith("#"))
        for num, px, py, ang in pins:
            sx, sy = sch_pin(x, y, px, py)
            net = netmap.get(num, None)
            if num not in netmap:
                raise SystemExit(f"{ref} pin {num} not assigned (use None for no connection)")
            if net is None:
                items.append(["no_connect", ["at", sx, sy], ["uuid", Q(uid())]])
                continue
            # stub outward from the body: the pin angle points from the connection toward the body
            d = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[int(ang) % 360]
            stub = 2 * G if (net in POWER_NETS and d[1] == 0) else G   # room for the power symbol
            ex, ey = round(sx + d[0] * stub, 2), round(sy + d[1] * stub, 2)
            items.append(["wire", ["pts", ["xy", sx, sy], ["xy", ex, ey]],
                          ["stroke", ["width", 0], ["type", "default"]], ["uuid", Q(uid())]])
            if net in POWER_NETS:
                power(net, ex, ey, ang)
            else:
                la = 180 if d[0] < 0 else (0 if d[0] > 0 else (270 if d[1] > 0 else 90))
                just = ["right", "bottom"] if la == 180 else ["left", "bottom"]
                items.append(["label", Q(net), ["at", ex, ey, la], ["fields_autoplaced", "yes"],
                              font(justify=just), ["uuid", Q(uid())]])
    for x, y, text, size in NOTES:
        items.append(["text", Q(text), ["exclude_from_sim", "no"], ["at", x, y, 0],
                      font(size, justify=["left", "bottom"]), ["uuid", Q(uid())]])
    sch = ["kicad_sch", ["version", 20250114], ["generator", Q("thermabrick_schematic_py")],
           ["generator_version", Q("9.0")], ["uuid", Q(root)], ["paper", Q("A3")],
           ["title_block", ["title", Q("ThermaBrick test article controller")], ["date", Q(DATE)],
            ["rev", Q(REV)], ["company", Q("Open Hardware Portfolio, amishchadha.com")],
            ["comment", 1, Q("TBK-DWG-003. Generated by electronics/src/schematic.py; do not edit by hand.")],
            ["comment", 2, Q("Licensed CERN-OHL-S-2.0")]],
           ["lib_symbols", *lib.values()], *items,
           ["sheet_instances", ["path", Q("/"), ["page", Q("1")]]]]
    return sch, lib


def write_project(sch, lib):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{NAME}.kicad_sch").write_text(dump(sch) + "\n", encoding="utf-8")
    symlib = ["kicad_symbol_lib", ["version", 20250114], ["generator", Q("thermabrick_schematic_py")],
              *[[e if i != 1 else Q(str(e).split(":", 1)[1]) for i, e in enumerate(v)]
                for k, v in lib.items() if k.startswith("TB:")]]
    (OUT / "thermabrick.kicad_sym").write_text(dump(symlib) + "\n", encoding="utf-8")
    (OUT / "sym-lib-table").write_text(
        '(sym_lib_table\n  (version 7)\n  (lib (name "TB")(type "KiCad")(uri "${KIPRJMOD}/thermabrick.kicad_sym")'
        '(options "")(descr "ThermaBrick project symbols"))\n)\n', encoding="utf-8")
    pro = {"meta": {"filename": f"{NAME}.kicad_pro", "version": 1}, "schematic": {"legacy_lib_dir": "", "legacy_lib_list": []},
           "sheets": [[str(sch[4][1]), "Root"]], "boards": [], "text_variables": {}}
    (OUT / f"{NAME}.kicad_pro").write_text(json.dumps(pro, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------- checks and exports
def kicad_cli():
    for c in (shutil.which("kicad-cli"), str(KICAD_APP / "Contents/MacOS/kicad-cli")):
        if c and Path(c).exists():
            return c
    return None


def check_and_export():
    cli = kicad_cli()
    if not cli:
        print("kicad-cli not found: schematic written, checks and exports skipped")
        return False
    sch = OUT / f"{NAME}.kicad_sch"
    erc = OUT / "erc.json"
    subprocess.run([cli, "sch", "erc", "--format", "json", "--severity-all", "-o", str(erc), str(sch)],
                   check=True, capture_output=True)
    report = json.loads(erc.read_text())
    viol = [v for s in report.get("sheets", []) for v in s.get("violations", [])]
    errors = [v for v in viol if v.get("severity") == "error"]
    for v in viol:
        where = "; ".join(i.get("description", "") for i in v.get("items", []))
        print(f"  ERC {v['severity']}: {v['type']}: {v['description']} [{where}]")
    print(f"ERC: {len(errors)} errors, {len(viol) - len(errors)} warnings")
    erc.unlink()

    net = OUT / f"{NAME}.net"
    subprocess.run([cli, "sch", "export", "netlist", "-o", str(net), str(sch)], check=True, capture_output=True)
    tree = parse(net.read_text())[0]
    got = {}
    for n in find(find(tree, "nets")[0], "net"):
        name = str(find(n, "name")[0][1]).lstrip("/")
        members = {f"{find(x, 'ref')[0][1]}.{find(x, 'pin')[0][1]}" for x in find(n, "node")}
        members = {m for m in members if not m.startswith("#")}
        if members:
            got[name] = members
    net.unlink()
    want = expected_nets()
    bad = 0
    for name, members in want.items():
        match = [g for g, m in got.items() if m == members]
        if not match:
            bad += 1
            near = max(got.items(), key=lambda kv: len(kv[1] & members))
            print(f"  NET MISMATCH {name}: want {sorted(members)}, closest {near[0]} {sorted(near[1])}")
    extra = [g for g, m in got.items() if not any(m == w for w in want.values()) and len(m) > 1]
    for g in extra:
        print(f"  UNEXPECTED NET {g}: {sorted(got[g])}")
    print(f"netlist: {len(want)} nets expected, {len(want) - bad} match, {len(extra)} unexpected")

    subprocess.run([cli, "sch", "export", "pdf", "-o", str(OUT / f"{NAME}.pdf"), str(sch)], check=True, capture_output=True)
    svg_dir = OUT / "_svg"
    subprocess.run([cli, "sch", "export", "svg", "--exclude-drawing-sheet", "--no-background-color", "-o", str(svg_dir), str(sch)],
                   check=True, capture_output=True)
    return len(errors) == 0 and bad == 0 and not extra


def build_sheet():
    """Place the KiCad SVG (no frame) on the portfolio ANSI B sheet as TBK-DWG-003."""
    svgs = list((OUT / "_svg").glob("*.svg"))
    if not svgs:
        return
    sys.path.insert(0, str(ROOT / ".kit"))
    from drawing import Sheet, M, TB_Y, W
    svg = svgs[0]
    txt = svg.read_text()
    # crop the A3 page to the drawn area so the circuit fills the sheet
    txt = re.sub(r'viewBox="[^"]*"', 'viewBox="15 15 390 200"', txt, count=1)
    cropped = OUT / "_svg" / "cropped.svg"
    cropped.write_text(txt)
    s = Sheet(project="ThermaBrick", title="Test article controller schematic", dwg_no="TBK-DWG-003", rev=REV,
              author="Amish Chadha", date=DATE, scale=None, units="n/a",
              material="Electrical schematic. KiCad source in electronics/test-article; see bom/bom-test-article.csv",
              revisions=[("P1", "First issue: test article controller", DATE, "AC")])
    s.scale = 1.0
    s.add_svg(cropped, M + 4, M + 16, W - 2 * M - 8, TB_Y - M - 20)
    s.save(ROOT / "cad" / "drawings" / "TBK-DWG-003")
    shutil.rmtree(OUT / "_svg")
    print("wrote cad/drawings/TBK-DWG-003 (SVG, PDF, PNG)")


def main():
    sch, lib = build()
    write_project(sch, lib)
    print(f"wrote {OUT.relative_to(ROOT)}/{NAME}.kicad_sch ({len(PARTS)} parts, {len(expected_nets())} nets)")
    ok = check_and_export()
    build_sheet()
    if not ok and kicad_cli():
        sys.exit(1)


if __name__ == "__main__":
    main()
