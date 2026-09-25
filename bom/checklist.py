#!/usr/bin/env python3
"""Generate bom/purchasing-checklist.md from the test article and controller board BOMs.

Run from the repo root:  python bom/checklist.py

Every BOM line must be assigned to a purchase group in GROUP below, and the checklist
totals must equal the BOM totals; the script fails otherwise, so the checklist cannot
drift from the BOM. Licensed MIT (see LICENSE-SOFTWARE).
"""
import csv
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "purchasing-checklist.md"

# Purchase groups, in the order to place them. Long-lead and single-source items first.
GROUPS = [
    ("import", "1. Made-to-order heaters (order first)",
     "Made-to-order cartridge heaters take two to four weeks. Order them the day the build is approved."),
    ("uline", "2. Uline", "Ships in one to three days."),
    ("refractory", "3. Kiln or refractory supplier", "Local pottery or kiln suppliers stock K-23 brick; call ahead."),
    ("digikey", "4. DigiKey or Mouser", "One order."),
    ("amazon", "5. Amazon or an electrical wholesaler", "Controls, wiring and small parts. Buy from sellers with easy returns."),
    ("local", "6. Home Depot or Lowe's (one trip)", "Pipe, sheet metal, insulation and sand."),
]
GROUP = {
    "Nichrome heating elements": "import",
    "Steel drum": "uline",
    "Insulating firebrick": "refractory",
    "12 V supply": "digikey", "Pull-down resistors": "digikey",
    "Inlet blower": "amazon", "Blower driver": "amazon", "Buck converter": "amazon", "ESP32 controller": "amazon",
    "Thermocouple amplifier": "amazon", "K-type thermocouples": "amazon", "Solid state relay": "amazon",
    "SSR heat sink": "amazon", "Independent high limit": "amazon", "Latching power relay": "amazon",
    "Start and stop buttons": "amazon", "Control enclosure": "amazon", "DIN rail": "amazon",
    "Cable glands": "amazon", "Lever connectors and PE stud": "amazon",
    "Sand": "local", "Heater well pipe": "local", "U-tube legs": "local", "U-tube elbow": "local",
    "U-tube bottom nipple": "local", "Dilution stack": "local", "Stone wool batt": "local", "Jacket sheet": "local",
    "Jacket fasteners and tape": "local", "Fuse": "local", "Supply cord": "local", "Heater junction box": "local",
}

# What to confirm before paying (order) and when the part arrives (arrival)
CHECKS = {
    "Nichrome heating elements": ("5/8 in (15.9 mm) diameter, 18 in long, 120 V, 250 W, 16 in heated with the 2 in cold "
                                  "end at the lead end, leads 24 in or longer rated for high temperature.",
                                  "Measure each cold resistance: 55 to 60 ohm, all four within 5 % of each other."),
    "Steel drum": ("Open head with bolt ring, unlined interior (Uline S-19411).",
                   "No liner or interior coating. Remove the lid gasket before first firing."),
    "Insulating firebrick": ("K-23 insulating firebrick, not dense firebrick.", "Light enough to lift easily; about 0.8 kg each."),
    "12 V supply": ("Mean Well HDR-15-12, or an equal DIN-rail 12 V supply of 1.25 A or more.", ""),
    "Pull-down resistors": ("10 kOhm, 1/4 W. Skip if an assortment is on hand.", ""),
    "Inlet blower": ("12 V, 0.8 A or less, 97 x 94 x 33 mm. High-speed 2 A to 3 A versions overload the supply.",
                     "Run it on 12 V and measure the current."),
    "Blower driver": ("Logic-level MOSFET module rated 5 A or more.", ""),
    "Buck converter": ("12 V in, 5 V out, 3 A.", "Set or check 5.0 V out before connecting the ESP32."),
    "ESP32 controller": ("Any ESP32-WROOM-32 board exposing GPIO 4, 5, 16, 17, 18, 19, 22, 25 and 26. For the optional "
                         "controller board, a genuine 38-pin ESP32-DevKitC V4 only.", ""),
    "Thermocouple amplifier": ("MAX6675 modules, pack of five.", "Pin order GND, VCC, SCK, CS, SO (required for the optional board)."),
    "K-type thermocouples": ("Type K, mineral insulated, ungrounded junction, 3 mm sheath, 500 mm.",
                             "Check with a multimeter that neither lead is connected to the sheath."),
    "Solid state relay": ("Zero-cross, DC control 3 to 32 V, AC load, 25 A.",
                          "Counterfeits are common. Test it switching a lamp from a 3.3 V and a 5 V control signal."),
    "SSR heat sink": ("Panel mount with thermal pad, sized for one SSR.", ""),
    "Independent high limit": ("REX-C100 with relay output (R*AN code), type K input, 100 to 240 VAC supply.",
                               "Confirm the output is a relay, not an SSR driver, before panel cutting."),
    "Latching power relay": ("JQX-30F 2Z, DPDT, 120 VAC coil (not 220 VAC or 12 VDC), with DIN-rail socket.", ""),
    "Start and stop buttons": ("22 mm, one red normally closed (STOP) and one green normally open (START), rated 120 VAC.",
                               "Check contact states with a multimeter."),
    "Control enclosure": ("Polycarbonate, 250 x 200 x 150 mm or larger, UL 94 V-0 or 5VA, IP65, with a mounting plate.",
                          "Inside depth 140 mm or more (TBK-DWG-005)."),
    "DIN rail": ("TS35 x 7.5.", ""),
    "Cable glands": ("Nylon, IP68, with locknuts: one M16, two M20, one M25.", ""),
    "Lever connectors and PE stud": ("Two 5-way lever connectors (Wago 221-415 or equal); M5 earth stud with ring lugs.", ""),
    "Sand": ("Washed play sand. Avoid all-purpose or leveling sand, which contains clay.", "Weigh each bag."),
    "Heater well pipe": ("3/4 in black steel, not galvanized, 10 ft.", ""),
    "U-tube legs": ("1-1/4 in x 36 in black steel nipples, not galvanized.", ""),
    "U-tube elbow": ("1-1/4 in black malleable iron 90 deg elbows.", ""),
    "U-tube bottom nipple": ("1-1/4 in x 6 in black steel nipple.", ""),
    "Dilution stack": ("4 in single-wall black stovepipe, 24 in, not galvanized.", ""),
    "Stone wool batt": ("ROCKWOOL Comfortbatt R15, 3.5 in, unfaced.", ""),
    "Jacket sheet": ("Aluminum roll flashing, 20 in x 25 ft.", ""),
    "Jacket fasteners and tape": ("Aluminum foil tape and sheet metal screws.", ""),
    "Fuse": ("Inline holder with 10 A fast-acting fuse; buy a spare fuse.", ""),
    "Supply cord": ("14/3 SJT with NEMA 5-15 plug, 6 ft.", ""),
    "Heater junction box": ("Steel handy box; ceramic terminal block rated 250 V, 10 A or more.", ""),
}

TOOLS = [
    "Multimeter with continuity and resistance ranges",
    "Bathroom scale (0.1 kg graduation)",
    "Vise, pipe cutter for 3/4 in pipe, and pipe wrenches",
    "Drill with hole saws or step drill: 22.5 mm (buttons), 28.7 mm and 44.2 mm (drum lid), 16.5, 20.5 and 25.5 mm (glands)",
    "Jigsaw or nibbler and file for the 45 x 45 mm REX-C100 cutout",
    "Tin snips and pop rivet gun",
    "Stopwatch and 159 L (42 gal) contractor bags for the airflow calibration",
    "Contact or infrared thermometer for jacket and stack surfaces (all five MAX6675 channels are in use)",
    "Insulation tester at 500 V, borrowed or rented, for TBK-TST-001 TP2",
    "P100 or N95 respirator, gloves and eye protection for sand and mineral wool",
]


def load(name):
    return list(csv.DictReader(open(HERE / name, encoding="utf-8")))


def money(v):
    return f"${v:,.2f}"


def main():
    rows = load("bom-test-article.csv")
    board = load("bom-controller-board.csv")
    missing = [r["item"] for r in rows if r["item"] not in GROUP]
    if missing:
        sys.exit(f"not assigned to a purchase group: {missing}")
    total = round(sum(float(r["qty"]) * float(r["unit_cost_usd"]) for r in rows), 2)

    L = ["# Purchasing checklist", "",
         "Test article (TBK-PRC-002), accepted budget $635.70. Generated from `bom-test-article.csv` and "
         "`bom-controller-board.csv` by `bom/checklist.py`; regenerate after any BOM change instead of editing this file.",
         "",
         "Prices are the BOM's budgetary estimates (US list prices, September 2026, before tax and shipping). "
         "Record the price actually paid beside each line.", "",
         "Tick an item's box when it is ordered, and its **Received** box once it has arrived and passed its check.", ""]
    check_total = 0.0
    for key, title, note in GROUPS:
        items = [r for r in rows if GROUP[r["item"]] == key]
        sub = round(sum(float(r["qty"]) * float(r["unit_cost_usd"]) for r in items), 2)
        check_total += sub
        L += [f"## {title}", "", f"{note} Subtotal {money(sub)}.", ""]
        for r in items:
            qty, unit = float(r["qty"]), float(r["unit_cost_usd"])
            order, arrival = CHECKS.get(r["item"], ("", ""))
            L.append(f"- [ ] **{r['item']}**, qty {r['qty']}, {money(unit)} each, {money(qty * unit)}. "
                     f"Supplier: {r['supplier']}.")
            if order:
                L.append(f"  - Specify: {order}")
            L.append(f"  - [ ] Received: {arrival or 'quantity and specification match the order.'}")
        L.append("")
    if round(check_total, 2) != total:
        sys.exit(f"checklist total {check_total} does not match BOM total {total}")
    L += [f"**Test article total: {money(total)}** across {len(rows)} lines.", ""]

    btotal = round(sum(float(r["qty"]) * float(r["unit_cost_usd"]) for r in board), 2)
    L += ["## Optional: controller board (TBK-DWG-004)", "",
          f"Only if building the controller on the printed board. Parts {money(btotal)}; the board replaces the buck "
          "converter and blower driver above ($6.00), so skip those two lines. Upload "
          "`electronics/controller-board/thermabrick-controller-board-gerbers-P1.zip` to the board house: 2 layers, "
          "1.6 mm FR-4, 1 oz copper, HASL, any color.", ""]
    for r in board:
        qty, unit = float(r["qty"]), float(r["unit_cost_usd"])
        L.append(f"- [ ] **{r['item']}**, qty {r['qty']}, {money(unit)} each, {money(qty * unit)}. "
                 f"{r['spec']}. Supplier: {r['supplier']}.")
        L.append("  - [ ] Received: quantity and specification match the order.")
    L += ["", "## Tools and safety equipment (not in the budget)", ""]
    L += [f"- [ ] {t}" for t in TOOLS]
    L += ["", "## Before building", "",
          "- [ ] Every Received box ticked and every arrival check passed.",
          "- [ ] Heater resistances recorded for TBK-TST-001 TP0.",
          "- [ ] Firmware built and host unit tests passing (`pio test -e native` in `firmware/`).",
          "- [ ] Analysis self-test passing (`python docs/05-tests/tbk_tst_001_fit.py selftest`).", ""]
    OUT.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {OUT.relative_to(HERE.parent)}: {len(rows)} lines, total {money(total)}")


if __name__ == "__main__":
    main()
