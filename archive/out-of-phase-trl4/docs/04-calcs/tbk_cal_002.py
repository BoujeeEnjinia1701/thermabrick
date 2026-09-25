#!/usr/bin/env python3
"""TBK-CAL-002 sizing calculations for the ThermaBrick reduced-scale test article.

Run from the repo root:  python docs/04-calcs/tbk_cal_002.py
Geometry comes from cad/src/test_article.py. The physics (sand properties, radial cell
model, heater sheath, U-tube air side) is reused unchanged from tbk_cal_001.py, so the
test article exercises exactly the models it is built to validate.

Licensed MIT (see LICENSE-SOFTWARE).
"""
import sys
from math import pi, log
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "cad" / "src"))

import tbk_cal_001 as base  # noqa: E402
from test_article import PARAMS as TA, derived as ta_derived  # noqa: E402

D = ta_derived()
# Point the shared models at the test article. The U-tube length uses the leg span.
base.P = {**TA, "leg_inner_r": 0.0, "leg_outer_r": TA["leg_span"]}
base.D = D
base.N_HEATERS = D["n_heaters"]
base.P_HEATER = TA["heater_w"]
base.FIG = HERE / "fig"

T_AMB, T_LO, T_HI = base.T_AMB, base.T_LO, base.T_HI
V_BLOWER_MAX = 4.0     # L/s through the U-tube, limited by the 12 V blower at about 110 Pa


def win(T, E):
    return (base.h_sand(T) - base.h_sand(T_LO)) / (base.h_sand(T_HI) - base.h_sand(T_LO)) * E


def standby(T_s=T_HI, h_out=6.0, eps_out=0.9):
    """Steady loss of the test article, same method as TBK-CAL-001 section 5."""
    k_mw, k_ifb, SIGMA = base.k_mw, base.k_ifb, base.SIGMA
    r0 = D["drum_r_o"] / 1000
    r2 = D["jacket_r_i"] / 1000
    H = (D["jacket_top_z"] - TA["base_h"]) / 1000
    A_end = pi * r0 ** 2

    def hs(Ts):
        Tk, Ta = Ts + 273.15, T_AMB + 273.15
        return h_out + eps_out * SIGMA * (Tk ** 2 + Ta ** 2) * (Tk + Ta)

    def solve(layers, A_outer):
        temps = list(np.linspace(T_s, T_AMB + 10, len(layers) + 1))
        for _ in range(100):
            Rs = [R(0.5 * (temps[i] + temps[i + 1])) for i, R in enumerate(layers)]
            Q = (T_s - T_AMB) / (sum(Rs) + 1 / (hs(temps[-1]) * A_outer))
            new = [T_s]
            for r in Rs:
                new.append(new[-1] - Q * r)
            temps = [0.5 * (x + y) for x, y in zip(temps, new)]
        return Q, temps

    Q_side, T_side = solve([lambda T: log(r2 / r0) / (2 * pi * k_mw(T) * H)], 2 * pi * r2 * H)
    t_int, t_top = D["ins_top_int"] / 1000, TA["ins_top"] / 1000
    Q_top, T_top = solve([lambda T: t_int / (k_mw(T) * A_end), lambda T: t_top / (k_mw(T) * A_end)],
                         pi * r2 ** 2)
    # Base: bricks on edge carry the drum; stone wool fills between. Parallel paths.
    bl, bw, bh = (v / 1000 for v in TA["brick"])
    A_b = TA["n_bricks"] * bl * bw * 0.5          # half of each brick lies under the drum
    A_w = A_end - A_b
    Q_base_b, _ = solve([lambda T: bh / (k_ifb(T) * A_b)], A_b)
    Q_base_w, _ = solve([lambda T: bh / (k_mw(T) * A_w)], A_w)
    # Pipe bridges: two U-tube legs to above the jacket; heater leads only for the wells
    L_pen = (D["jacket_top_z"] - D["sand_top_z"]) / 1000
    A40 = pi / 4 * ((TA["tube_od"] / 1000) ** 2 - (TA["tube_id"] / 1000) ** 2)
    Q_legs = 2 * base.K_STEEL * A40 * (T_s - T_AMB) / L_pen
    Q_leads = D["n_heaters"] * 2 * 70.0 * 2.08e-6 * (T_s - T_AMB) / (TA["ins_top"] / 1000)
    total = Q_side + Q_top + Q_base_b + Q_base_w + Q_legs + Q_leads
    return dict(Q_side=Q_side, T_side=T_side, Q_top=Q_top, Q_base=Q_base_b + Q_base_w,
                Q_legs=Q_legs, Q_leads=Q_leads, total=total)


def cooldown(hours=24):
    m, T, E_lost = TA["sand_mass_kg"], T_HI, 0.0
    for _ in range(hours * 6):
        Q = standby(T)["total"]
        E_lost += Q * 600
        target = base.h_sand(T) - Q * 600 / m
        lo, hi = 20.0, T
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if base.h_sand(mid) < target else (lo, mid)
        T = 0.5 * (lo + hi)
    return E_lost / 3.6e6, T


def mass():
    m = TA["sand_mass_kg"] + 12.0                       # 16 gal drum, 20 ga, with lid and ring
    m += D["n_heaters"] * 1.68 * (D["well_top_z"] - D["floor_z"]) / 1000
    m += 3.39 * (2 * (D["leg_top_z"] - D["floor_z"]) + TA["leg_span"]) / 1000 + 1.2
    m += 12.0 + 4 * 1.2 + 4.0 + D["n_heaters"] * 0.4   # wool, bricks, jacket and stack, heaters
    return m


def main():
    s = base.storage()
    print("== 1. Storage")
    for k in ("m", "E", "vol_L", "depth", "depth_eq", "area"):
        print(f"  {k:9s} {s[k]:9.3f}")
    full = 18.337
    print(f"  scale to full size {s['E'] / full:.3f}")

    print("== 2. Charge, 4 x 250 W at 120 V")
    LOSS = lambda T: standby(T)["total"]  # noqa: E731
    ch = base.charge(p_heater=TA["heater_w"], loss=LOSS)
    ch0 = base.charge(p_heater=TA["heater_w"])
    print(f"  adiabatic reference (as the full-scale cell model): full at {ch0['log'][-1][0]:.2f} h")
    lg = ch["log"]
    t_ = np.array([r[0] for r in lg])
    print(f"  r1 {ch['r1']*1000:.2f} mm  r2 {ch['r2']*1000:.1f} mm  (full scale 79.7 mm)  L {ch['L']*1000:.0f} mm")
    for hrs in (2, 4, 6):
        Pw = np.interp(hrs, t_, [base.N_HEATERS * r[1] / 1000 for r in lg])
        Tm = float(np.interp(hrs, t_, [r[4] for r in lg]))
        print(f"  {hrs} h: {Pw:.2f} kW, Tmean {Tm:.0f} C, {win(Tm, s['E']):.2f} kWh")
    t_lim = next((r[0] for r in lg if r[1] < TA["heater_w"] - 1), None)
    print(f"  full at {lg[-1][0]:.2f} h; wall limit from {t_lim:.2f} h; peak sheath {max(r[3] for r in lg):.0f} C; "
          f"end power {base.N_HEATERS * lg[-1][1]:.0f} W; near/far {lg[-1][5]:.0f}/{lg[-1][6]:.0f} C")

    print("== 3. Discharge, one U-tube, blower max 4 L/s")
    rows = {}
    for Qd in (150.0, 250.0, 325.0):
        dc = base.discharge(Q_demand=Qd, V_max_Ls=V_BLOWER_MAX, loss=LOSS)
        lgd = dc["log"]
        t_hold = next((r[0] for r in lgd if r[1] < Qd - 5), lgd[-1][0])
        T_hold = next((r[4] for r in lgd if r[1] < Qd - 5), lgd[-1][4])
        rows[Qd] = dc
        print(f"  demand {Qd:.0f} W: held {t_hold:.1f} h to Tmean {T_hold:.0f} C; delivered {dc['E_out']:.2f} kWh "
              f"in {lgd[-1][0]:.1f} h; peak outlet {max(r[3] for r in lgd):.0f} C; r2 {dc['r2']*1000:.0f} mm")
    ap = base.air_path(V_hx_Ls=V_BLOWER_MAX)
    print(f"  U-tube pressure drop at {V_BLOWER_MAX} L/s: {ap['dp_hx']:.0f} Pa")

    print("== 4. Standby")
    sb = standby()
    for k in ("Q_side", "Q_top", "Q_base", "Q_legs", "Q_leads", "total"):
        print(f"  {k:8s} {sb[k]:6.1f} W")
    print(f"  side temps {[round(t) for t in sb['T_side']]}")
    print(f"  at 300 C {standby(300)['total']:.0f} W; at 150 C {standby(150)['total']:.0f} W")
    el, T24 = cooldown()
    print(f"  24 h idle from full: {el:.2f} kWh lost ({el / s['E'] * 100:.0f} %), sand {T24:.0f} C")

    print("== 5. Electrical, 120 V")
    R = 120.0 ** 2 / TA["heater_w"]
    I = base.N_HEATERS * 120.0 / R
    print(f"  R {R:.1f} ohm each; total {I:.2f} A, {base.N_HEATERS * TA['heater_w']:.0f} W; 15 A circuit, 12 A continuous")
    print(f"  watt density {TA['heater_w'] / (pi * TA['heater_d'] / 1000 * TA['heater_heated_len'] / 1000) / 1e4:.2f} W/cm2")
    print("== 6. Mass")
    m = mass()
    print(f"  {m:.0f} kg; brick edge bearing {m * 9.81 / (TA['n_bricks'] * TA['brick'][1] * 8e-6) / 1e6:.2f} MPa "
          f"(chime lip 8 mm wide on the 64 mm brick edge)")

    # Figures
    lg = ch["log"]
    t = [r[0] for r in lg]
    base.svg_chart(base.FIG / "tbk-cal-002-fig1-charge.svg", "Test article charge from 150 °C mean at up to 1.0 kW",
                   "Time (h)", 10,
                   [(t, [base.N_HEATERS * r[1] / 1000 for r in lg], "Heater power (kW)", False, 0.8)],
                   [(t, [r[4] for r in lg], "Sand mean (°C)", False, 0.3), (t, [r[2] for r in lg], "Well wall (°C)", True, 0.6)],
                   "Power (kW)", (0, 1.2), "Temperature (°C)", (100, 600))
    lg = rows[250.0]["log"]
    t = [r[0] for r in lg]
    base.svg_chart(base.FIG / "tbk-cal-002-fig2-discharge.svg", "Test article discharge at 250 W demand from 450 °C mean",
                   "Time (h)", 24,
                   [(t, [r[1] / 1000 for r in lg], "Heat output (kW)", False, 0.85)],
                   [(t, [r[4] for r in lg], "Sand mean (°C)", False, 0.3), (t, [r[3] for r in lg], "Exchanger outlet (°C)", True, 0.5)],
                   "Power (kW)", (0, 0.5), "Temperature (°C)", (0, 500))


if __name__ == "__main__":
    main()
