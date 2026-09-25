#!/usr/bin/env python3
"""Start a build log entry from build-log/TEMPLATE.md.

Run from the repo root:
    python build-log/new_entry.py "Drum preparation" --stage B
    python build-log/new_entry.py "Charge run" --stage TP3
    python build-log/new_entry.py "Sourcing trip" --date 2026-10-02

Writes build-log/YYYY-MM-DD-short-title.md with the header filled in and the record table
for the stage (build stages A to L of docs/07-build/test-article-build.md, or TBK-TST-001
procedures TP0 to TP6), then adds the entry to the index in build-log/README.md, newest
first. Standard library only. Licensed MIT (see LICENSE-SOFTWARE).
"""
import argparse
import datetime as dt
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
README = HERE / "README.md"
MARK_A, MARK_B = "<!-- index start -->", "<!-- index end -->"

STAGES = {
    "A": "Incoming checks", "B": "Drum preparation", "C": "Wells and U-tube", "D": "Thermocouples",
    "E": "Base and drum", "F": "Internals and sand", "G": "Heaters", "H": "Insulation and jacket",
    "I": "Blower and stack", "J": "Controller enclosure", "K": "Checks unplugged", "L": "First power-up",
    "TP0": "Inspection and instrument checks", "TP1": "Limit and fault response, cold",
    "TP2": "Bake-out and commissioning", "TP3": "Charge", "TP4": "Cool-down", "TP5": "Discharge",
    "TP6": "Cycling",
}

# (quantity, expected) rows for each stage's record table
RECORDS = {
    "A": [(f"Heater H{i} cold resistance", "55 to 60 Ω, all within 5 %") for i in range(1, 5)]
         + [(f"Probe T{i} lead to sheath", "Open (ungrounded)") for i in range(1, 5)]
         + [("Probe polarity checked, T1 to T6", "Reading rises when the tip is warmed")],
    "B": [("Lid holes drilled, C3", "Six holes at the C3 positions and diameters"),
          ("Thermocouple holes, C4", "Three 4 mm holes"), ("Sand level marked, C5", "491 mm above the inner floor")],
    "C": [(f"Well W{i} length after cutting", "692 mm (C1)") for i in range(1, 5)]
         + [("Crimps closed and folded", "No gap"), ("U-tube leg spacing at the lid", "206 ± 2 mm")],
    "D": [("T1 tip height on W1", "300 mm above the inner floor"), ("T2 tip height on W3", "300 mm"),
          ("T3 tip height, axis", "300 mm"), ("T4 tip height and position", "300 mm at C4 x, y")],
    "E": [("Brick centers from the axis", "150 mm, radial at 45°, 135°, 225° and 315°"), ("Drum level", "Level both ways")],
    "F": [("Sand mass poured", "68 kg"), ("Sand depth", "491 mm"), ("Probes still at their marks", "Yes")],
    "G": [(f"Heater H{i} seated on the crimp", "Yes") for i in range(1, 5)],
    "H": [("Headspace insulation depth", "170 mm"), ("Side insulation layers", "3, joints staggered"),
          ("Jacket overlap", "50 mm"), ("Drum bonded to the heater cable PE", "Yes")],
    "I": [("Blower sealed to the inlet leg", "Yes"), ("Outlet leg inside the stack", "40 mm"),
          ("Clearance to combustibles around the stack", "450 mm or more")],
    "J": [("Cutouts and glands to C11", "Yes"), ("Every C12 net wired", "Yes"),
          ("Thermocouple joints type K throughout", "Yes")],
    "K": [("Earth continuity to each bonded part", "0.5 Ω or less"),
          ("Heater load, L_HEAT to N", "14 to 15 Ω"), ("Heater insulation to earth", "Open"),
          ("Mains L to N, START not pressed", "Not a short"), ("Coil path, L to K1 A1", "Open"),
          ("+12V to GND", "Not shorted"), ("SSR input to GND", "About 10 kΩ")],
    "L": [("GFCI test trip", "Trips and resets"), ("12 V rail", "11.5 to 12.5 V"), ("Buck output", "5.0 V"),
          ("K1 latches on START, drops on STOP", "Yes"), ("K1 stays open after power loss", "Yes"),
          ("Firmware commit flashed", "Recorded"), ("v_line and r_heat set", "Measured values"),
          ("T1, T3 to T6 at room temperature", "Within 2 K of each other and of T2"),
          ("Blower at 50 % duty", "Air out of the stack")],
}
TEST_ROWS = [("Firmware commit", "From the logger file header"), ("Data file", "docs/05-tests/data/YYYY-MM-DD_TPn.csv"),
             ("Line voltage, start and end", "V"), ("Channel offsets applied", "From TP0"),
             ("Pass criteria (TBK-TST-001)", "Pass or fail, with the value")]
for k in ("TP0", "TP1", "TP2", "TP3", "TP4", "TP5", "TP6"):
    RECORDS[k] = TEST_ROWS


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]


def repo_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=HERE, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def main():
    ap = argparse.ArgumentParser(description="Start a build log entry")
    ap.add_argument("title")
    ap.add_argument("--stage", choices=sorted(STAGES), help="build stage A to L or test procedure TP0 to TP6")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--author", default="Amish Chadha")
    a = ap.parse_args()

    path = HERE / f"{a.date}-{slug(a.title)}.md"
    if path.exists():
        raise SystemExit(f"{path.name} already exists")
    t = (HERE / "TEMPLATE.md").read_text(encoding="utf-8")
    stage = (f"Build stage {a.stage}, {STAGES[a.stage]}" if a.stage and not a.stage.startswith("TP")
             else f"TBK-TST-001 {a.stage}, {STAGES[a.stage]}" if a.stage else "")
    t = t.replace("# YYYY-MM-DD: Short title", f"# {a.date}: {a.title}", 1)
    t = t.replace("| Date | YYYY-MM-DD |", f"| Date | {a.date} |", 1)
    t = t.replace("| Author | |", f"| Author | {a.author} |", 1)
    if stage:
        t = re.sub(r"\| Stage or procedure \| .* \|", f"| Stage or procedure | {stage} |", t, count=1)
    c = repo_commit()
    if c:
        t = t.replace("| Repo commit | `git rev-parse --short HEAD` at the start of the session |", f"| Repo commit | `{c}` |", 1)
    if a.stage:
        rows = "\n".join(f"| {q} | {e} | | |" for q, e in RECORDS[a.stage])
        t = t.replace("| Quantity | Expected | Measured | OK |\n| --- | --- | --- | --- |\n| | | | |",
                      "| Quantity | Expected | Measured | OK |\n| --- | --- | --- | --- |\n" + rows, 1)
    path.write_text(t, encoding="utf-8")

    r = README.read_text(encoding="utf-8")
    line = f"- [{a.date}: {a.title}]({path.name})" + (f" ({stage})" if stage else "")
    i, j = r.index(MARK_A) + len(MARK_A), r.index(MARK_B)
    entries = [e for e in r[i:j].strip().splitlines() if e.startswith("- [")]
    entries = sorted(entries + [line], reverse=True)          # newest first
    README.write_text(r[:i] + "\n" + "\n".join(entries) + "\n" + r[j:], encoding="utf-8")
    print(f"wrote build-log/{path.name} and updated the index")


if __name__ == "__main__":
    main()
