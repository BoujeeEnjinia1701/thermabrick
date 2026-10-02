#!/usr/bin/env python3
"""TBK-CAL-001 sizing calculations for ThermaBrick.

Run from the repo root:  python docs/04-calcs/tbk_cal_001.py
Geometry comes from cad/src/model.py (PARAMS), so the numbers in TBK-CAL-001
always match the CAD model. The script prints every value quoted in the note.

Licensed MIT (see LICENSE-SOFTWARE).
"""
import copy
import sys
from math import pi, log, exp, sqrt
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "cad" / "src"))
from model import PARAMS as P, derived  # noqa: E402

D = derived()
SIGMA = 5.670e-8
T_AMB = 20.0           # room air, deg C
T_LO, T_HI = 150.0, 450.0  # usable sand window, deg C (energy-weighted mean)


# ---------------------------------------------------------------- properties
def cp_quartz(T):
    """Specific heat of alpha quartz, J/(kg K). NIST Shomate fit, 298 to 847 K."""
    t = (np.asarray(T) + 273.15) / 1000
    A, B, C, Dd, E = -6.076591, 251.6755, -324.7964, 168.5604, 0.002548
    return (A + B * t + C * t**2 + Dd * t**3 + E / t**2) / 0.0600843


def h_sand(T, T0=20.0):
    """Sensible enthalpy of sand above T0, J/kg (trapezoid integration of cp)."""
    x = np.linspace(T0, T, 400)
    return np.trapezoid(cp_quartz(x), x)


K_SCALE = 1.0          # sensitivity multiplier on sand conductivity


def k_sand(T):
    """Effective conductivity of dry packed silica sand, W/(m K). Conservative linear fit."""
    return K_SCALE * (0.27 + 2.1e-4 * (np.asarray(T) - 20.0))


def k_aes(Tm):     # AES blanket, 128 kg/m^3
    return 0.035 + 1.0e-4 * Tm + 1.5e-7 * Tm**2


def k_mw(Tm):      # stone wool batt or board
    return 0.035 + 1.0e-4 * Tm + 1.3e-7 * Tm**2


def k_ifb(Tm):     # K-23 insulating firebrick
    return 0.12 + 1.0e-4 * Tm


def air(T):
    """Dry air at 1 atm: rho kg/m^3, cp J/(kg K), k W/(m K), mu Pa s, Pr."""
    Tk = T + 273.15
    rho = 101325 / (287.05 * Tk)
    cp = 1002 + 0.12 * (T - 20) if T > 20 else 1005.0
    mu = 1.458e-6 * Tk**1.5 / (Tk + 110.4)
    k = 2.646e-3 * Tk**1.5 / (Tk + 245.4 * 10 ** (-12 / Tk))
    return rho, cp, k, mu, cp * mu / k


# ---------------------------------------------------------------- 1. storage
def storage():
    m = P["sand_mass_kg"]
    dh = h_sand(T_HI) - h_sand(T_LO)
    E = m * dh / 3.6e6
    cp_mean = dh / (T_HI - T_LO)
    m_req = 18.0 * 3.6e6 / dh
    return dict(m=m, dh_kJkg=dh / 1e3, cp_mean=cp_mean, E=E, m_req=m_req,
                E_cp080=m * 800 * (T_HI - T_LO) / 3.6e6,
                cp20=float(cp_quartz(20)), cp150=float(cp_quartz(150)), cp450=float(cp_quartz(450)),
                vol_L=D["sand_vol_m3"] * 1000, depth=D["sand_depth"], depth_eq=D["sand_depth_eq"],
                area=D["sand_area_m2"])


# ---------------------------------------------------------------- 2. radial cell model
class Cell:
    """1D radial finite-volume model of the sand around one pipe (unit length).

    Inner boundary: prescribed heat flux into (charge) or out of (discharge) the sand at r1.
    Outer boundary: adiabatic at r2, the radius of the pipe's equal-area share of the bed.
    """

    def __init__(self, r1, r2, T0, n=60):
        self.r1, self.r2 = r1, r2
        f = np.linspace(0, 1, n + 1) ** 1.6                # finer near the pipe
        self.rf = r1 + (r2 - r1) * f                       # faces
        self.rc = 0.5 * (self.rf[1:] + self.rf[:-1])       # centers
        self.V = pi * (self.rf[1:] ** 2 - self.rf[:-1] ** 2)  # m^3 per m
        self.T = np.full(n, float(T0))
        self.rho = P["sand_rho"]

    def step(self, q_in, dt, q_out=0.0):
        """Advance dt with q_in W per m entering the sand at r1 (negative = extraction) and
        q_out W per m leaving at r2 (standby loss, spread over the cells)."""
        T, rc, rf, V = self.T, self.rc, self.rf, self.V
        n = len(T)
        C = self.rho * cp_quartz(T) * V / dt
        kf = k_sand(0.5 * (T[1:] + T[:-1]))
        G = 2 * pi * kf / np.log(rc[1:] / rc[:-1])       # W/(m K) between centers
        a = np.zeros(n); b = C.copy(); c = np.zeros(n); d = C * T
        b[:-1] += G; b[1:] += G
        a[1:] = -G; c[:-1] = -G
        d[0] += q_in
        d[-1] -= q_out
        # Thomas algorithm
        for i in range(1, n):
            w = a[i] / b[i - 1]
            b[i] -= w * c[i - 1]
            d[i] -= w * d[i - 1]
        x = np.empty(n)
        x[-1] = d[-1] / b[-1]
        for i in range(n - 2, -1, -1):
            x[i] = (d[i] - c[i] * x[i + 1]) / b[i]
        self.T = x

    def T_wall(self, q_in, h_contact):
        """Pipe outer-wall temperature: extrapolate to r1, then add the contact resistance."""
        T0 = self.T[0]
        k0 = float(k_sand(T0))
        dT_cond = q_in / (2 * pi * k0) * log(self.rc[0] / self.r1)
        return T0 + dT_cond + q_in / (h_contact * 2 * pi * self.r1)

    def energy(self, T0=20.0):
        """Sensible energy above T0, J per m, integrating cp over each cell."""
        return float(sum(self.rho * v * h_sand(t, T0) for v, t in zip(self.V, self.T)))

    def mean_equiv(self):
        """Uniform temperature that holds the same energy (energy-weighted mean)."""
        e = self.energy() / (self.rho * self.V.sum())
        lo, hi = 20.0, 900.0
        for _ in range(40):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if h_sand(mid) < e else (lo, mid)
        return 0.5 * (lo + hi)


H_CONTACT = 300.0      # W/(m^2 K), pipe wall to packed sand (sensitivity case: 150)
EPS_SHEATH, EPS_WELL = 0.80, 0.70
T_SHEATH_MAX = 700.0   # controller limit on the heater's internal thermocouple (element rated 760)
T_WALL_MAX = 550.0     # controller limit on the well-wall thermocouple (quartz inversion at 573)
P_HEATER = P["heater_w"]  # W per cartridge at 240 V
N_HEATERS = D["n_heaters"]


def sheath_temp(q_per_m, T_well, well_id=None):
    """Heater sheath temperature from radiation and gas conduction across the well gap."""
    rs, rw = P["heater_d"] / 2000, (well_id or P["well_id"]) / 2000
    eps = 1 / (1 / EPS_SHEATH + rs / rw * (1 / EPS_WELL - 1))
    lo, hi = T_well, T_well + 1500
    for _ in range(60):
        Ts = 0.5 * (lo + hi)
        _, _, k_g, _, _ = air(0.5 * (Ts + T_well))
        q = 2 * pi * rs * SIGMA * eps * ((Ts + 273.15) ** 4 - (T_well + 273.15) ** 4) \
            + 2 * pi * k_g * (Ts - T_well) / log(rw / rs)
        lo, hi = (Ts, hi) if q < q_per_m else (lo, Ts)
    return 0.5 * (lo + hi)


def charge(T_start=T_LO, dt=120.0, t_max=30 * 3600, h_contact=None, n=None, well=None, p_heater=None,
           loss=None):
    """Charge one heater cell from a uniform T_start until its energy-weighted mean reaches T_HI.

    Each step the controller applies the largest power that keeps the well wall at or below
    T_WALL_MAX and the sheath at or below T_SHEATH_MAX at the end of the step. With loss (a
    function of mean sand temperature returning W for the whole unit), the standby loss is
    drawn from the outer edge of every cell."""
    h_contact = h_contact or H_CONTACT
    n = n or N_HEATERS
    well_od, well_id = well or (P["well_od"], P["well_id"])
    p_heater = p_heater or 3000.0 / n
    L = D["sand_depth_eq"] / 1000                  # heat spreads over the full bed depth
    L_h = P["heater_heated_len"] / 1000            # sheath check uses the heated length
    r1 = well_od / 2000
    r2 = sqrt((D["sand_area_m2"] / n + pi * r1 ** 2) / pi)
    cell = Cell(r1, r2, T_start)
    E_target = cell.rho * cell.V.sum() * h_sand(T_HI)
    q_max = p_heater / L
    t, log_ = 0.0, []
    while t < t_max:
        q_loss = loss(cell.mean_equiv()) / (n * L) if loss else 0.0
        lo, hi = 0.0, q_max
        for _ in range(18):
            q = 0.5 * (lo + hi)
            trial = copy.deepcopy(cell)
            trial.step(q, dt, q_loss)
            Tw = trial.T_wall(q, h_contact)
            ok = Tw <= T_WALL_MAX and sheath_temp(q * L / L_h, Tw, well_id) <= T_SHEATH_MAX
            lo, hi = (q, hi) if ok else (lo, q)
        q = lo
        cell.step(q, dt, q_loss)
        t += dt
        Tw = cell.T_wall(q, h_contact)
        log_.append((t / 3600, q * L * n / N_HEATERS, Tw, sheath_temp(q * L / L_h, Tw, well_id), cell.mean_equiv(),
                     float(cell.T[0]), float(cell.T[-1])))
        if cell.energy() >= E_target:
            break
    return dict(r1=r1, r2=r2, L=L, log=log_, cell=cell)


def utube_air(m_dot, T_wall):
    """Air side of one U-tube at mass flow m_dot (kg/s) with uniform inner-wall temperature.

    Returns outlet temperature, duty (W), inside h and Reynolds number."""
    Di = P["tube_id"] / 1000
    Lu = 2 * D["sand_depth"] / 1000 + (P["leg_outer_r"] - P["leg_inner_r"]) / 1000
    T_out = T_AMB
    for _ in range(4):                                   # properties at the mean air temperature
        Tm = 0.5 * (T_AMB + T_out)
        rho, cp, k, mu, Pr = air(Tm)
        Re = 4 * m_dot / (pi * Di * mu)

        def nu_lam(re):          # Hausen, developing flow, constant wall temperature
            gz = re * Pr * Di / Lu
            return 3.66 + 0.0668 * gz / (1 + 0.04 * gz ** (2 / 3))

        def nu_turb(re):         # Gnielinski
            f = (0.790 * log(re) - 1.64) ** -2
            return (f / 8) * (re - 1000) * Pr / (1 + 12.7 * sqrt(f / 8) * (Pr ** (2 / 3) - 1))
        if Re <= 2300:
            Nu = nu_lam(Re)
        elif Re >= 4000:
            Nu = nu_turb(Re)
        else:                    # linear blend through the transition range
            g = (Re - 2300) / 1700
            Nu = (1 - g) * nu_lam(2300) + g * nu_turb(4000)
        h = Nu * k / Di
        T_out = T_wall - (T_wall - T_AMB) * exp(-h * pi * Di * Lu / (m_dot * cp))
    return T_out, m_dot * cp * (T_out - T_AMB), h, Re, Lu


def discharge(Q_demand=1000.0, V_max_Ls=25.0, T_start=T_HI, dt=60.0, t_max=60 * 3600, loss=None):
    """Discharge the bed at Q_demand (W total) through the six U-tubes, limited by V_max_Ls
    of room air (L/s at 20 C) through the exchanger. One cell per tube leg."""
    n_legs = 2 * P["n_utubes"]
    r1 = P["tube_od"] / 2000
    r2 = sqrt((D["sand_area_m2"] / n_legs + pi * r1 ** 2) / pi)
    cell = Cell(r1, r2, T_start)
    rho20 = air(20)[0]
    m_max = V_max_Ls / 1000 * rho20 / P["n_utubes"]
    Lu = utube_air(m_max, 100)[4]
    L_cell = 2 * D["sand_depth_eq"] / 1000   # sand per tube is accounted over the two legs' depth
    t, log_, E_out = 0.0, [], 0.0
    while t < t_max:
        def duty(m):
            # wall temperature consistent with the extracted flux (one fixed-point pass is enough here)
            Tw = cell.T[0]
            for _ in range(3):
                _, Q, _, _, _ = utube_air(m, Tw)
                q = Q / L_cell
                Tw = cell.T_wall(-q, H_CONTACT)
            return Q, Tw
        Qmax, _ = duty(m_max)
        if P["n_utubes"] * Qmax <= Q_demand:
            m = m_max
        else:
            lo, hi = 1e-5, m_max
            for _ in range(30):
                mid = 0.5 * (lo + hi)
                lo, hi = (mid, hi) if P["n_utubes"] * duty(mid)[0] < Q_demand else (lo, mid)
            m = hi
        Q, Tw = duty(m)
        T_out = utube_air(m, Tw)[0]
        Tm = cell.mean_equiv()
        log_.append((t / 3600, P["n_utubes"] * Q, m * P["n_utubes"] / rho20 * 1000, T_out, Tm))
        if Tm <= T_LO:
            break
        q_loss = loss(Tm) / (n_legs * L_cell / 2) if loss else 0.0
        cell.step(-Q / L_cell, dt, q_loss)
        E_out += P["n_utubes"] * Q * dt
        t += dt
    return dict(r1=r1, r2=r2, Lu=Lu, log=log_, E_out=E_out / 3.6e6)


# ---------------------------------------------------------------- 3. standby loss
K_STEEL, K_SS = 45.0, 18.0      # W/(m K) near 300 C, carbon steel and type 304


def k_mp(Tm):      # microporous silica panel (option only)
    return 0.020 + 2.0e-5 * Tm


def standby(T_s=T_HI, h_out=6.0, eps_out=0.9, ss_legs=False, microporous_mm=0.0):
    """Steady heat loss with the sand at T_s. Series resistances with k at each layer's mean
    temperature, plus axial conduction along the pipes that cross the top insulation.
    Options: a microporous hot-face layer of microporous_mm replaces the same thickness of AES;
    ss_legs makes the part of each inlet leg above the lid a 1-1/4 in Sch 10 type 304 nipple."""
    r0 = D["drum_r_o"] / 1000
    t_mp = microporous_mm / 1000
    r_mp = r0 + t_mp
    r1 = r0 + P["ins_side_aes"] / 1000
    r2 = r1 + P["ins_side_mw"] / 1000
    H_side = (D["jacket_top_z"] - D["base_h"]) / 1000
    A_end = pi * r0 ** 2
    A_out_end = pi * r2 ** 2

    def surface_h(Ts):
        Tk, Ta = Ts + 273.15, T_AMB + 273.15
        return h_out + eps_out * SIGMA * (Tk ** 2 + Ta ** 2) * (Tk + Ta)

    def solve(layers, T_hot, A_outer):
        """layers: resistance functions R(T_mean) in K/W, hot to cold. Fixed point on temperatures."""
        temps = list(np.linspace(T_hot, T_AMB + 10, len(layers) + 1))
        for _ in range(100):
            Rs = [R(0.5 * (temps[i] + temps[i + 1])) for i, R in enumerate(layers)]
            R_tot = sum(Rs) + 1 / (surface_h(temps[-1]) * A_outer)
            Q = (T_hot - T_AMB) / R_tot
            new = [T_hot]
            for r in Rs:
                new.append(new[-1] - Q * r)
            temps = [0.5 * (x + y) for x, y in zip(temps, new)]
        return Q, temps

    # Side: optional microporous, AES blanket, stone wool batts; cylindrical
    side = []
    if t_mp:
        side.append(lambda T: log(r_mp / r0) / (2 * pi * k_mp(T) * H_side))
    side += [lambda T: log(r1 / r_mp) / (2 * pi * k_aes(T) * H_side),
             lambda T: log(r2 / r1) / (2 * pi * k_mw(T) * H_side)]
    Q_side, T_side = solve(side, T_s, 2 * pi * r2 * H_side)

    # Top: AES then stone wool in the drum headspace, lid, AES and stone wool above the lid
    t_int = D["ins_top_int"] / 1000
    top = [lambda T: 0.050 / (k_aes(T) * A_end),
           lambda T: (t_int - 0.050) / (k_mw(T) * A_end),
           lambda T: P["ins_top_aes"] / 1000 / (k_aes(T) * A_end),
           lambda T: P["ins_top_mw"] / 1000 / (k_mw(T) * A_end)]
    Q_top, T_top = solve(top, T_s, A_out_end)

    # Base: drum floor to floor through AES board, firebrick and stone wool board
    base = [lambda T: P["base_aes"] / 1000 / (k_aes(T) * A_end),
            lambda T: P["base_ifb"] / 1000 / (k_ifb(T) * A_end),
            lambda T: P["base_mw"] / 1000 / (k_mw(T) * A_end)]
    Q_base, T_base = solve(base, T_s, A_out_end)

    def bar(od, idd, k_m, L, dT):
        """Axial conduction along a pipe wall across the insulation. The insulation around the
        pipe carries nearly the same gradient, so side exchange is neglected."""
        return k_m * pi / 4 * (od ** 2 - idd ** 2) * dT / L

    # Heater wells end at the lid, under the top insulation. Only the leads cross it:
    # two 14 AWG nickel conductors per heater (k about 70 W/(m K), 2.08 mm^2).
    L_top = (D["jacket_top_z"] - D["top_ins_z0"]) / 1000
    Q_wells = N_HEATERS * 2 * 70.0 * 2.08e-6 * (T_s - T_AMB) / L_top
    # Inlet legs cross the headspace stack and the top insulation to the plenum on the jacket.
    L_head = (D["top_ins_z0"] - D["sand_top_z"]) / 1000
    A40 = pi / 4 * ((P["tube_od"] / 1000) ** 2 - (P["tube_id"] / 1000) ** 2)
    A10 = pi / 4 * ((P["tube_od"] / 1000) ** 2 - 0.0366 ** 2)
    R_leg = L_head / (K_STEEL * A40) + L_top / ((K_SS * A10) if ss_legs else (K_STEEL * A40))
    Q_legs = P["n_utubes"] * (T_s - T_AMB) / R_leg
    # Outlet legs end in the collector. Heat leaves it through the 0.6 mm stovepipe outlet
    # and the thinner insulation over the collector; the heat-trap bend stops convection.
    L_over = (D["jacket_top_z"] - D["top_ins_z0"] - P["collector_h"]) / 1000
    A_col = pi * (P["collector_d"] / 2000) ** 2
    T_col = T_s - 60.0
    Q_out = bar(P["outlet_d"] / 1000, P["outlet_d"] / 1000 - 0.0012, K_STEEL, L_over, T_col - T_AMB) \
        + A_col * (T_col - T_AMB) / (L_over / float(k_mw((T_col + T_AMB) / 2)))
    bridges = Q_wells + Q_legs + Q_out
    total = Q_side + Q_top + Q_base + bridges
    return dict(Q_side=Q_side, T_side=T_side, Q_top=Q_top, T_top=T_top, Q_base=Q_base, T_base=T_base,
                Q_wells=Q_wells, Q_legs=Q_legs, Q_out=Q_out, bridges=bridges, total=total,
                A_side=2 * pi * r2 * H_side)


def retention(**opts):
    """Energy lost over 24 h idle from full charge, stepping the loss with sand temperature."""
    m = P["sand_mass_kg"]
    T = T_HI
    E_lost = 0.0
    for _ in range(24 * 6):
        Q = standby(T, **opts)["total"]
        E_lost += Q * 600
        target = h_sand(T) - Q * 600 / m
        lo, hi = 20.0, T
        for _ in range(30):
            mid = 0.5 * (lo + hi)
            lo, hi = (mid, hi) if h_sand(mid) < target else (lo, mid)
        T = 0.5 * (lo + hi)
    return E_lost / 3.6e6, T


# ---------------------------------------------------------------- 4. electrical
def electrical():
    V = 240.0
    R = V ** 2 / P_HEATER
    n = N_HEATERS
    I_group = n / 2 * V / R                       # two SSR groups, each half the heaters in parallel
    I_total = n * V / R
    ssr_loss = 1.2 * I_group                      # W, typical 1.2 V on-state drop
    heated = P["heater_heated_len"] / 1000
    wd = P_HEATER / (pi * P["heater_d"] / 1000 * heated) / 1e4
    return dict(R=R, I_group=I_group, I_total=I_total, P_total=n * P_HEATER, ssr_loss=ssr_loss,
                breaker=20, cont_limit=0.8 * 20, watt_density=wd, watt_density_in2=wd * 6.4516)


# ---------------------------------------------------------------- 5. air path and fan
def air_path(V_hx_Ls=25.0, Q=1000.0, T_supply=50.0):
    rho20 = air(20)[0]
    m_tube = V_hx_Ls / 1000 * rho20 / P["n_utubes"]
    Di = P["tube_id"] / 1000
    A = pi / 4 * Di ** 2
    # hot leg: evaluate at a representative 250 C outlet; cold leg at 20 C
    dp = 0.0
    Lleg = D["sand_depth"] / 1000 + 0.45
    for T, L, K in ((20.0, Lleg + 0.08, 0.5 + 1.5), (250.0, Lleg + 0.08, 1.5 + 1.0)):
        rho, cp, k, mu, Pr = air(T)
        v = m_tube / (rho * A)
        Re = rho * v * Di / mu
        f = 0.25 / (np.log10(0.045e-3 / (3.7 * Di) + 5.74 / Re ** 0.9)) ** 2
        dp += (f * L / Di + K) * rho * v ** 2 / 2
    v20 = m_tube / (rho20 * A)
    m_supply = Q / (air(35)[1] * (T_supply - T_AMB))
    V_supply = m_supply / air(T_supply)[0] * 1000
    return dict(dp_hx=dp, v_inlet=v20, V_supply=V_supply, V_supply_cfm=V_supply * 2.119,
                V_hx_cfm=V_hx_Ls * 2.119, V_boost=1.5 * V_supply)


# ---------------------------------------------------------------- 6. structure
def mass_and_floor():
    m_sand = P["sand_mass_kg"]
    m_drum = 26.0                      # 18 ga open-head drum with lid and ring, catalog weight
    m_wells = N_HEATERS * 1.68 * (D["well_top_z"] - D["floor_z"]) / 1000   # 3/4 in Sch 40: 1.68 kg/m
    leg_m = (D["jacket_top_z"] - D["floor_z"]) / 1000 * 2 + 0.16
    m_tubes = P["n_utubes"] * (3.39 * leg_m + 2 * 0.6)                     # 1-1/4 in Sch 40: 3.39 kg/m + elbows
    m_ins = 80.0                       # AES, stone wool, firebrick and board (estimate); +5 kg for the base batt ring and two more bricks (TBK-DDR-003)
    m_jacket = 20.0                    # jacket, plenum, collector, duct stubs
    m_heaters = N_HEATERS * 0.45
    total = m_sand + m_drum + m_wells + m_tubes + m_ins + m_jacket + m_heaters
    A_foot = pi * (D["jacket_r_o"] / 1000) ** 2
    A_drum = pi * (D["drum_r_o"] / 1000) ** 2
    return dict(total=total, kPa_foot=total * 9.81 / A_foot / 1000,
                kPa_drum=(total - m_jacket) * 9.81 / A_drum / 1000,
                m_wells=m_wells, m_tubes=m_tubes)


# ---------------------------------------------------------------- figures
FIG = Path(__file__).resolve().parent / "fig"


def svg_chart(path, title, xlabel, xmax, left, right, ylabel_l, ylim_l, ylabel_r, ylim_r):
    """Minimal two-axis line chart in the portfolio style. left/right: [(xs, ys, label, dashed)]."""
    W, H, ml, mr, mt, mb = 160.0, 88.0, 16.0, 16.0, 10.0, 14.0
    pw, ph = W - ml - mr, H - mt - mb
    ink, muted, rule, accent = "#111827", "#4B5563", "#D1D5DB", "#0F766E"
    font = "IBM Plex Sans, Helvetica, Arial, sans-serif"
    X = lambda x: ml + pw * x / xmax
    Yl = lambda y: mt + ph * (1 - (y - ylim_l[0]) / (ylim_l[1] - ylim_l[0]))
    Yr = lambda y: mt + ph * (1 - (y - ylim_r[0]) / (ylim_r[1] - ylim_r[0]))
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}mm" height="{H}mm" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>']
    t = lambda x, y, s, a="middle", c=muted, sz=2.6, w=400: o.append(
        f'<text x="{x:.2f}" y="{y:.2f}" font-family="{font}" font-size="{sz}" font-weight="{w}" fill="{c}" '
        f'text-anchor="{a}">{s}</text>')
    for i in range(6):
        y = mt + ph * i / 5
        o.append(f'<line x1="{ml}" y1="{y:.2f}" x2="{ml + pw}" y2="{y:.2f}" stroke="{rule}" stroke-width="0.2"/>')
        t(ml - 1.5, y + 0.9, f"{ylim_l[1] - (ylim_l[1] - ylim_l[0]) * i / 5:g}", "end")
        t(ml + pw + 1.5, y + 0.9, f"{ylim_r[1] - (ylim_r[1] - ylim_r[0]) * i / 5:g}", "start")
    step = 2 if xmax <= 12 else 4
    for xv in range(0, int(xmax) + 1, step):
        t(X(xv), mt + ph + 4, f"{xv}")
    o.append(f'<rect x="{ml}" y="{mt}" width="{pw}" height="{ph}" fill="none" stroke="{ink}" stroke-width="0.3"/>')
    t(ml + pw / 2, H - 3, xlabel)
    t(ml, mt - 3, ylabel_l, "start", accent, 2.6, 500)
    t(ml + pw, mt - 3, ylabel_r, "end", ink, 2.6, 500)
    t(W / 2, 4.5, title, "middle", ink, 3.0, 600)
    for series, Y, color in ((left, Yl, accent), (right, Yr, ink)):
        for xs, ys, label, dashed, *frac in series:
            pts = " ".join(f"{X(x):.2f},{Y(y):.2f}" for x, y in zip(xs, ys))
            dash = ' stroke-dasharray="1.6 1"' if dashed else ""
            o.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="0.5"{dash}/>')
            j = int((len(xs) - 1) * (frac[0] if frac else 0.66))
            t(X(xs[j]), Y(ys[j]) - 1.8, label, "middle", color, 2.4, 500)
    o.append("</svg>")
    FIG.mkdir(exist_ok=True)
    Path(path).write_text("".join(o))


def figures(ch, dc):
    lg = ch["log"]
    t = [r[0] for r in lg]
    svg_chart(FIG / "tbk-cal-001-fig1-charge.svg", "Charge from 150 °C mean at up to 3.0 kW",
              "Time (h)", 8,
              [(t, [N_HEATERS * r[1] / 1000 for r in lg], "Heater power (kW)", False, 0.8)],
              [(t, [r[4] for r in lg], "Sand mean (°C)", False, 0.3), (t, [r[2] for r in lg], "Well wall (°C)", True, 0.6)],
              "Power (kW)", (0, 3.5), "Temperature (°C)", (100, 600))
    lg = dc["log"]
    t = [r[0] for r in lg]
    svg_chart(FIG / "tbk-cal-001-fig2-discharge.svg", "Discharge at 1.0 kW demand from 450 °C mean",
              "Time (h)", 18,
              [(t, [r[1] / 1000 for r in lg], "Heat output (kW)", False, 0.8)],
              [(t, [r[4] for r in lg], "Sand mean (°C)", False, 0.3), (t, [r[3] for r in lg], "Exchanger outlet (°C)", True, 0.5)],
              "Power (kW)", (0, 2.0), "Temperature (°C)", (0, 500))


def sensitivity():
    """Charge time and 6 h energy for the main uncertain inputs."""
    global K_SCALE
    win = lambda T: (h_sand(T) - h_sand(T_LO)) / (h_sand(T_HI) - h_sand(T_LO)) * storage()["E"]
    rows = []
    for label, ks, hc in (("Base case", 1.0, None), ("Sand k x 0.8", 0.8, None), ("Sand k x 1.25", 1.25, None),
                          ("Contact h 150 W/(m2 K)", 1.0, 150.0)):
        K_SCALE = ks
        lg = charge(h_contact=hc, loss=LOSS)["log"]
        r6 = min(lg, key=lambda r: abs(r[0] - 6))
        dcl = discharge(loss=LOSS)["log"]
        t_rated = next((r[4] for r in dcl if r[1] < 990), dcl[-1][4])
        rows.append((label, lg[-1][0], win(r6[4]), t_rated))
    K_SCALE = 1.0
    return rows


def win_kwh(T):
    """Heat in the usable window at uniform sand mean T, kWh."""
    return (h_sand(T) - h_sand(T_LO)) / (h_sand(T_HI) - h_sand(T_LO)) * storage()["E"]


# ---------------------------------------------------------------- report
def LOSS(T):
    """Standby loss of the whole unit at mean sand temperature T, W."""
    return standby(T)["total"]


def main():
    s = storage()
    print("== 0. Adiabatic reference (v0.1 basis, no standby loss)")
    lg0 = charge()["log"]
    dc0 = discharge()
    t0 = next((r[0] for r in dc0["log"] if r[1] < 990), dc0["log"][-1][0])
    print(f"  full charge {lg0[-1][0]:.2f} h; 1.0 kW held {t0:.2f} h")
    print("== 1. Storage")
    for k, v in s.items():
        print(f"  {k:10s} {v:10.3f}")

    print("== 2. Charge (one heater cell), standby loss coupled")
    ch = charge(loss=LOSS)
    print(f"  r1 {ch['r1']*1000:.1f} mm  r2 {ch['r2']*1000:.1f} mm  L {ch['L']*1000:.0f} mm")
    lg = ch["log"]
    for row in lg[:: max(1, len(lg) // 14)] + [lg[-1]]:
        t, Pw, Tw, Ts, Tm, Tin, Tout = row
        print(f"  t {t:5.2f} h  P/heater {Pw:6.1f} W  total {N_HEATERS*Pw/1000:5.2f} kW  Twall {Tw:5.0f}  "
              f"Tsheath {Ts:5.0f}  Tmean {Tm:5.1f}  Tnear {Tin:5.0f}  Tfar {Tout:5.0f}")
    win = lambda T: (h_sand(T) - h_sand(T_LO)) / (h_sand(T_HI) - h_sand(T_LO)) * s["E"]
    for hrs in (2, 4, 6, 8):
        r = min(lg, key=lambda r: abs(r[0] - hrs))
        print(f"  after {hrs} h: Tmean {r[4]:.0f} C, stored {win(r[4]):.1f} kWh of window")
    t_full = lg[-1][0]
    E80 = next(r[0] for r in lg if r[4] >= T_LO + 0.8 * (T_HI - T_LO))
    E50 = next(r[0] for r in lg if r[4] >= T_LO + 0.5 * (T_HI - T_LO))
    t_derate = next((r[0] for r in lg if r[1] < P_HEATER - 1), None)
    print(f"  full at {t_full:.2f} h, 80 % window at {E80:.2f} h, 50 % at {E50:.2f} h, "
          f"power limit starts at {t_derate} h")
    # energy absorbed in the first 6 h
    print(f"  mean power over full charge {s['E'] / t_full:.2f} kW")

    print("== 3. Discharge at 1.0 kW, 25 L/s max through the exchanger")
    dc = discharge(loss=LOSS)
    lg = dc["log"]
    print(f"  r1 {dc['r1']*1000:.1f} mm  r2 {dc['r2']*1000:.1f} mm  U-tube length {dc['Lu']:.2f} m")
    for row in lg[:: max(1, len(lg) // 14)] + [lg[-1]]:
        t, Q, V, Tout, Tm = row
        print(f"  t {t:5.2f} h  Q {Q:6.0f} W  V_hx {V:5.1f} L/s  T_out {Tout:5.0f}  Tmean {Tm:5.1f}")
    t_rated = next((r[0] for r in lg if r[1] < 990), lg[-1][0])
    Tm_rated = next((r[4] for r in lg if r[1] < 990), lg[-1][4])
    print(f"  holds 1.0 kW for {t_rated:.2f} h, down to Tmean {Tm_rated:.0f} C; "
          f"energy delivered {dc['E_out']:.2f} kWh over {lg[-1][0]:.1f} h; "
          f"passive {s['E'] - dc['E_out']:.2f} kWh")
    for Tm_probe in (400, 300, 250, 200, 150):
        r = min(lg, key=lambda r: abs(r[4] - Tm_probe))
        print(f"    at Tmean {Tm_probe}: {r[1]:.0f} W")

    figures(ch, dc)
    print("== 3b. Boost 1.5 kW")
    dcb = discharge(Q_demand=1500.0, V_max_Ls=25.0, loss=LOSS)
    lg = dcb["log"]
    t_b = next((r[0] for r in lg if r[1] < 1490), lg[-1][0])
    Tm_b = next((r[4] for r in lg if r[1] < 1490), lg[-1][4])
    print(f"  holds 1.5 kW for {t_b:.2f} h, down to Tmean {Tm_b:.0f} C")

    print("== 4. Standby loss")
    sb = standby()
    for k in ("Q_side", "Q_top", "Q_base", "Q_wells", "Q_legs", "Q_out", "bridges", "total"):
        print(f"  {k:8s} {sb[k]:7.1f} W")
    print(f"  side temps {[round(t) for t in sb['T_side']]}  top {[round(t) for t in sb['T_top']]}  "
          f"base {[round(t) for t in sb['T_base']]}")
    sb300 = standby(300.0)
    sb150 = standby(150.0)
    print(f"  at 300 C {sb300['total']:.0f} W, at 150 C {sb150['total']:.0f} W")
    E_lost, T24 = retention()
    print(f"  24 h idle from full: lost {E_lost:.2f} kWh ({E_lost/s['E']*100:.1f} % of window), "
          f"sand {T24:.0f} C")
    print("  options at 450 C:")
    for label, o in (("stainless upper inlet legs", dict(ss_legs=True)),
                     ("25 mm microporous hot face", dict(microporous_mm=25.0)),
                     ("both", dict(ss_legs=True, microporous_mm=25.0))):
        r = standby(**o)
        el, _ = retention(**o)
        print(f"    {label:28s} {r['total']:6.0f} W  (side {r['Q_side']:.0f}, legs {r['Q_legs']:.0f})  "
              f"24 h loss {el:.1f} kWh")

    print("== 5. Electrical")
    for k, v in electrical().items():
        print(f"  {k:16s} {v:8.2f}")

    print("== 6. Air path")
    for k, v in air_path().items():
        print(f"  {k:14s} {v:8.2f}")

    print("== 7. Mass and floor load")
    for k, v in mass_and_floor().items():
        print(f"  {k:10s} {v:8.2f}")
    print("== 2b. Charge at exact hours (interpolated)")
    lg = ch["log"]
    for hrs in (2, 4, 6):
        t_ = np.array([r[0] for r in lg])
        Pw = np.interp(hrs, t_, [N_HEATERS * r[1] / 1000 for r in lg])
        Tm = float(np.interp(hrs, t_, [r[4] for r in lg]))
        print(f"  {hrs} h: {Pw:.2f} kW, Tmean {Tm:.0f} C, {win_kwh(Tm):.1f} kWh")
    print("== 2c. Heater layouts at 3.0 kW total (full charge h, kWh in 6 h)")
    for label, n, well in (("6 x 3/4 in", 6, (26.7, 20.9)), ("6 x 1-1/2 in", 6, (48.3, 40.9)),
                           ("9 x 3/4 in", 9, (26.7, 20.9)), ("12 x 3/4 in", 12, (26.7, 20.9)),
                           ("12 x 1 in", 12, (33.4, 26.6))):
        lg = charge(n=n, well=well, loss=LOSS)["log"]
        t_ = np.array([r[0] for r in lg])
        T6 = float(np.interp(6, t_, [r[4] for r in lg])) if t_[-1] >= 6 else T_HI
        print(f"  {label:14s} {lg[-1][0]:5.1f} h  {win_kwh(T6):5.1f} kWh")
    print("== 8. Sensitivity (full charge h, kWh in 6 h, sand mean where 1.0 kW ends)")
    for label, tf, e6, tr in sensitivity():
        print(f"  {label:26s} {tf:5.1f} h  {e6:5.1f} kWh  {tr:5.0f} C")
    print("== Geometry")
    for k in ("sand_depth", "sand_top_z", "ins_top_int", "jacket_r_o", "jacket_top_z", "overall_h", "overall_d"):
        print(f"  {k:12s} {D[k]:8.1f}")


if __name__ == "__main__":
    main()
