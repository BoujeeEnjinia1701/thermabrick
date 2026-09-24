#!/usr/bin/env python3
"""Logging host for the ThermaBrick test article (TBK-TST-001, section 12).

Polls the controller's /log endpoint every 5 s and appends new rows, with a wall-clock
time stamp, to docs/05-tests/data/YYYY-MM-DD_TPn.csv. The polling is also the heartbeat
the firmware needs: if this script stops for 60 s, the controller turns the heaters off.

Usage (from the repo root):
    python firmware/tools/logger.py --host 192.168.1.50 --token SECRET --procedure TP3 \
        --vline 119.6 --note "charge from 150 C"

Standard library only. Licensed MIT (see LICENSE-SOFTWARE).
"""
import argparse
import datetime as dt
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def get(host, path, token, **params):
    if token:
        params["token"] = token
    url = f"http://{host}{path}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=8) as r:
        return r.read().decode()


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", required=True, help="controller IP address or host name")
    ap.add_argument("--token", default="", help="API_TOKEN from secrets.h")
    ap.add_argument("--procedure", required=True, help="TBK-TST-001 procedure, e.g. TP3")
    ap.add_argument("--vline", type=float, help="line voltage measured at the start, V")
    ap.add_argument("--note", default="", help="free text for the file header")
    ap.add_argument("--out", default=str(ROOT / "docs" / "05-tests" / "data"))
    ap.add_argument("--interval", type=float, default=5.0)
    a = ap.parse_args()

    out_dir = Path(a.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{dt.date.today().isoformat()}_{a.procedure}.csv"

    status = json.loads(get(a.host, "/status", a.token))
    config = json.loads(get(a.host, "/config", a.token))
    since = status["seq"]            # start from now; earlier rows belong to other runs
    new_file = not path.exists()
    with path.open("a", encoding="utf-8") as f:
        if new_file:
            f.write(f"# ThermaBrick test article, TBK-TST-001 {a.procedure}\n")
            f.write(f"# started {dt.datetime.now().astimezone().isoformat(timespec='seconds')}\n")
            f.write(f"# firmware {status['fw']}\n")
            f.write(f"# config {json.dumps(config)}\n")
            if a.vline:
                f.write(f"# line voltage at start {a.vline} V\n")
            f.write("# channel offsets from TP0: record here before the run\n")
            if a.note:
                f.write(f"# note {a.note}\n")
            header_written = False
        else:
            f.write(f"# resumed {dt.datetime.now().astimezone().isoformat(timespec='seconds')} "
                    f"firmware {status['fw']}\n")
            header_written = True
        f.flush()
        print(f"logging to {path}; Ctrl-C to stop (the heaters will turn off within 60 s)")
        failures = 0
        while True:
            try:
                text = get(a.host, "/log", a.token, since=since)
                failures = 0
            except Exception as e:  # keep trying; the firmware protects itself
                failures += 1
                print(f"{dt.datetime.now():%H:%M:%S} poll failed ({failures}): {e}", file=sys.stderr)
                time.sleep(a.interval)
                continue
            lines = text.strip().splitlines()
            if not lines:
                time.sleep(a.interval)
                continue
            header, rows = lines[0], lines[1:]
            if not header_written:
                f.write("host_time," + header + "\n")
                header_written = True
            now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
            for row in rows:
                seq = int(row.split(",", 1)[0])
                if seq <= since:
                    continue
                if seq > since + 1 and since > 0:
                    f.write(f"# gap: rows {since + 1} to {seq - 1} lost\n")
                f.write(f"{now},{row}\n")
                since = seq
            f.flush()
            if rows:
                last = rows[-1].split(",")
                print(f"{now[11:19]} seq {last[0]} T1 {last[2]} T3 {last[3]} T4 {last[4]} "
                      f"duty {last[9]} faults {last[-1]}")
            time.sleep(a.interval)


if __name__ == "__main__":
    main()
