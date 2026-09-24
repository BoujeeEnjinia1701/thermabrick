#!/usr/bin/env python3
"""TBK-TST-001 analysis: fit the test article model to measured data.

Run from the repo root.

    Fit sand conductivity, wall contact conductance and insulation conductivity to a charge
    (TP3) and cool-down (TP4) record, and report the TP3 and TP4 pass criteria:
        python docs/05-tests/tbk_tst_001_fit.py fit --tp3 FILE --tp4 FILE

    Predict a discharge (TP5) with the fitted parameters, with no further fitting:
        python docs/05-tests/tbk_tst_001_fit.py tp5 --tp5 FILE [--params FILE]

    Check the method on synthetic data made with the TBK-CAL-002 model (a prerequisite
    in TBK-TST-001, section 13). Exits non-zero if the known parameters are not recovered:
        python docs/05-tests/tbk_tst_001_fit.py selftest

Input files are the CSVs written by firmware/tools/logger.py. Results are written as
JSON and SVG to docs/05-tests/results/. NumPy only. Licensed MIT (see LICENSE-SOFTWARE).
"""
import argparse
import csv
import datetime as dt
import json
import sys
from math import pi, sqrt, log
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "docs" / "04-calcs"))

import tbk_cal_002 as ta  # noqa: E402  (sets the shared models to the test article geometry)

base = ta.base
TA, D = ta.TA, ta.D
RESULTS = HERE / "results"

N_HEAT = D["n_heaters"]
L_EQ = D["sand_depth_eq"] / 1000                     # m, heater cell length basis
R1 = TA["well_od"] / 2000
R2 = sqrt((D["sand_area_m2"] / N_HEAT + pi * R1 ** 2) / pi)
R_T4 = 0.034                                          # T4: 34 mm from the W1 center
RHO = TA["sand_rho"]
T_WALL_MAX = 550.0
H_CONTACT_0 = base.H_CONTACT                         # 300 W/(m2 K)
T_LO, T_HI = base.T_LO, base.T_HI

# Enthalpy table for fast conversion between temperature and energy
T_TAB = np.linspace(0.0, 900.0, 1801)
H_TAB = np.concatenate([[0.0], np.cumsum(0.5 * (base.cp_quartz(T_TAB[1:]) + base.cp_quartz(T_TAB[:-1]))
                                         * np.diff(T_TAB))]) + float(base.h_sand(0.0, 20.0))  # zero at 20 C


def h_of(T):
    return np.interp(T, T_TAB, H_TAB)


def T_of(h):
    return np.interp(h, H_TAB, T_TAB)


# ---------------------------------------------------------------- parameters
class Params:
    """Values fitted by the analysis. Fitting works on their logarithms.

    k_sand and k_ins multiply the TBK-CAL-001 sand and insulation conductivities; h_contact is
    the wall contact conductance in W/(m2 K); p_scale corrects the logged heater power, which
    carries the +/-5 % line-voltage and resistance uncertainty of TBK-TST-001, Table 3. The
    cool-down fixes k_ins with no heater power, which is what lets p_scale be separated."""
    names = ("k_sand", "h_contact", "k_ins", "p_scale")

    def __init__(self, k_sand=1.0, h_contact=H_CONTACT_0, k_ins=1.0, p_scale=1.0):
        self.k_sand, self.h_contact, self.k_ins, self.p_scale = k_sand, h_contact, k_ins, p_scale

    @classmethod
    def from_x(cls, x):
        return cls(float(np.exp(x[0])), float(H_CONTACT_0 * np.exp(x[1])), float(np.exp(x[2])), float(np.exp(x[3])))

    def x(self):
        return np.array([log(self.k_sand), log(self.h_contact / H_CONTACT_0), log(self.k_ins), log(self.p_scale)])

    def as_dict(self):
        return {"k_sand": self.k_sand, "h_contact": self.h_contact, "k_ins": self.k_ins, "p_scale": self.p_scale}


def loss_table(k_ins):
    """Standby loss of the whole article (W) against mean sand temperature, with the stone wool
    and firebrick conductivities scaled by k_ins. Uses the TBK-CAL-002 envelope model."""
    k_mw0, k_ifb0 = base.k_mw, base.k_ifb
    base.k_mw = lambda Tm: k_ins * k_mw0(Tm)
    base.k_ifb = lambda Tm: k_ins * k_ifb0(Tm)
    try:
        Ts = np.linspace(20.0, 600.0, 30)
        Qs = np.array([ta.standby(float(T))["total"] if T > 20.5 else 0.0 for T in Ts])
    finally:
        base.k_mw, base.k_ifb = k_mw0, k_ifb0
    return Ts, Qs


# ---------------------------------------------------------------- forward model
class Bed:
    """Radial finite-volume model of one heater cell, as in TBK-CAL-001 (tbk_cal_001.Cell),
    rewritten with a fast enthalpy table so a fit can run it many times."""

    def __init__(self, p: Params, T0, n=40, r1=R1, r2=R2):
        self.p = p
        f = np.linspace(0, 1, n + 1) ** 1.6
        self.rf = r1 + (r2 - r1) * f
        self.rc = 0.5 * (self.rf[1:] + self.rf[:-1])
        self.V = pi * (self.rf[1:] ** 2 - self.rf[:-1] ** 2)
        self.r1 = r1
        self.T = np.full(n, float(T0)) if np.isscalar(T0) else np.array(T0, float)
        self.lnr = np.log(self.rc[1:] / self.rc[:-1])

    def k(self, T):
        return self.p.k_sand * (0.27 + 2.1e-4 * (T - 20.0))

    def step(self, q_in, q_out, dt):
        T = self.T
        n = len(T)
        C = RHO * base.cp_quartz(T) * self.V / dt
        G = 2 * pi * self.k(0.5 * (T[1:] + T[:-1])) / self.lnr
        b = C.copy()
        b[:-1] += G
        b[1:] += G
        d = C * T
        d[0] += q_in
        d[-1] -= q_out
        c = -G
        # Thomas algorithm (a[i] = c[i-1] = -G[i-1])
        cp_, dp_ = np.empty(n - 1), np.empty(n)
        cp_[0] = c[0] / b[0]
        dp_[0] = d[0] / b[0]
        for i in range(1, n):
            m = b[i] + G[i - 1] * (cp_[i - 1] if i - 1 < n - 1 else 0.0)
            if i < n - 1:
                cp_[i] = c[i] / m
            dp_[i] = (d[i] + G[i - 1] * dp_[i - 1]) / m
        x = np.empty(n)
        x[-1] = dp_[-1]
        for i in range(n - 2, -1, -1):
            x[i] = dp_[i] - cp_[i] * x[i + 1]
        self.T = x

    def t_wall(self, q_in):
        T0 = self.T[0]
        return T0 + q_in / (2 * pi * self.k(T0)) * log(self.rc[0] / self.r1) + q_in / (self.p.h_contact * 2 * pi * self.r1)

    def t_at(self, r):
        return float(np.interp(r, self.rc, self.T))

    def mean(self):
        return float(T_of(np.sum(self.V * h_of(self.T)) / self.V.sum()))

    def energy_j(self):
        """Stored heat of the whole bed above 20 C, J (all cells, equivalent depth)."""
        return float(RHO * np.sum(self.V * h_of(self.T)) * L_EQ * N_HEAT)


def simulate(p: Params, t, power, T0, dt=60.0, controller=False, t_end=None):
    """Run the heater cell model through a record.

    t, power: sample times (s from start) and total heater power (W). With controller=True the
    measured power is ignored and the model applies up to 1.0 kW, limited to a 550 C well
    wall, as the firmware does. Returns model time series at its own steps."""
    Tl, Ql = loss_table(p.k_ins)
    bed = Bed(p, T0)
    t_end = t_end if t_end is not None else t[-1]
    q_max = TA["heater_w"] / L_EQ
    out = {k: [] for k in ("t", "T1", "T3", "T4", "Tmean", "P", "loss", "E")}
    tk = 0.0
    while tk <= t_end + 1e-6:
        Tm = bed.mean()
        loss = float(np.interp(Tm, Tl, Ql))
        q_out = loss / (N_HEAT * L_EQ)
        if controller:
            lo, hi = 0.0, q_max
            for _ in range(14):
                q = 0.5 * (lo + hi)
                trial = Bed(p, bed.T)
                trial.step(q, q_out, dt)
                lo, hi = (q, hi) if trial.t_wall(q) <= T_WALL_MAX else (lo, q)
            q_in = lo
        else:
            # mean measured power over the coming step
            q_in = p.p_scale * float(np.interp(tk + dt / 2, t, power)) / (N_HEAT * L_EQ)
        for k, v in (("t", tk), ("T1", bed.t_wall(q_in)), ("T3", float(bed.T[-1])), ("T4", bed.t_at(R_T4)),
                     ("Tmean", Tm), ("P", q_in * N_HEAT * L_EQ), ("loss", loss), ("E", bed.energy_j())):
            out[k].append(v)
        bed.step(q_in, q_out, dt)
        tk += dt
    return {k: np.array(v) for k, v in out.items()}


# ---------------------------------------------------------------- data
COLS = ("T1_C", "T3_C", "T4_C", "T5_C", "T6_C", "heater_W", "airflow_Ls", "exchanger_W", "blower_duty")


def read_log(path):
    """Read a logger CSV. Returns time (s, from the first row) and a dict of float arrays
    (NaN where the firmware logged a blank field)."""
    rows = [r for r in csv.DictReader(line for line in open(path, encoding="utf-8") if not line.startswith("#"))]
    if not rows:
        raise SystemExit(f"{path}: no data rows")
    stamps = [dt.datetime.fromisoformat(r["host_time"]) for r in rows]
    t = np.array([(s - stamps[0]).total_seconds() for s in stamps])
    data = {c: np.array([float(r[c]) if r.get(c) not in (None, "") else np.nan for r in rows]) for c in COLS}
    return stamps[0], t, data


def join(first, second):
    """Join TP3 and TP4 records on the wall clock. The heaters are taken as off in any gap."""
    s0, t0, d0 = first
    s1, t1, d1 = second
    offset = (s1 - s0).total_seconds()
    gap = offset - t0[-1]
    if gap > 600:
        print(f"note: {gap / 60:.0f} min gap between records; heaters taken as off in the gap")
    t = np.concatenate([t0, t1 + offset])
    d = {c: np.concatenate([d0[c], d1[c]]) for c in COLS}
    return t, d, t0[-1]


def measured_energy_j(T1, T4, T3):
    """Stored heat estimated from the measured temperatures alone: piecewise-linear radial
    profile through T1 (well wall), T4 (34 mm) and T3 (cell edge), integrated over the cell
    with the quartz enthalpy. Independent of the fitted model state, but approximate: T1 sits
    above the sand by the contact drop, so the estimate reads a little high. Used only for the
    closure check."""
    bed = Bed(Params(), 150.0)
    r = bed.rc
    out = np.full(len(T1), np.nan)
    for i in range(len(T1)):
        if np.isnan(T1[i]) or np.isnan(T4[i]) or np.isnan(T3[i]):
            continue
        prof = np.interp(r, [R1, R_T4, R2], [T1[i], T4[i], T3[i]])
        out[i] = RHO * np.sum(bed.V * h_of(prof)) * L_EQ * N_HEAT
    return out


# ---------------------------------------------------------------- fitting
def residuals(x, t, d, T0, stride=6):
    """Measured minus modeled T1, T4 and T3, K, every `stride` rows (60 s at 10 s logging)."""
    sim = simulate(Params.from_x(x), t, np.nan_to_num(d["heater_W"]), T0)
    idx = np.arange(0, len(t), stride)
    res = []
    for ch, key in (("T1_C", "T1"), ("T4_C", "T4"), ("T3_C", "T3")):
        meas = d[ch][idx]
        mod = np.interp(t[idx], sim["t"], sim[key])
        ok = ~np.isnan(meas)
        res.append(meas[ok] - mod[ok])
    return np.concatenate(res), sim


def levenberg_marquardt(fun, x0, lo, hi, max_iter=20, h=0.02):
    x = np.array(x0, float)
    r, _ = fun(x)
    ssr = float(r @ r)
    lam = 1e-2
    for it in range(max_iter):
        J = np.empty((len(r), len(x)))
        for j in range(len(x)):
            xp = x.copy()
            xp[j] += h
            J[:, j] = (fun(xp)[0] - r) / h
        A, g = J.T @ J, J.T @ r
        improved = False
        for _ in range(8):
            step = np.linalg.solve(A + lam * np.diag(np.diag(A) + 1e-9), -g)
            xn = np.clip(x + step, lo, hi)
            rn, _ = fun(xn)
            ssr_n = float(rn @ rn)
            if ssr_n < ssr:
                improved = True
                break
            lam *= 10
        print(f"  iteration {it + 1}: RMS {sqrt(ssr / len(r)):.2f} K -> {sqrt(ssr_n / len(rn)):.2f} K, "
              f"params {np.round(np.exp(xn), 3)}")
        if not improved:
            break
        rel = (ssr - ssr_n) / ssr
        x, r, ssr = xn, rn, ssr_n
        lam = max(lam / 10, 1e-6)
        if rel < 1e-5:
            break
    # Covariance from the final Jacobian
    J = np.empty((len(r), len(x)))
    for j in range(len(x)):
        xp = x.copy()
        xp[j] += h
        J[:, j] = (fun(xp)[0] - r) / h
    dof = max(len(r) - len(x), 1)
    s2 = ssr / dof
    cov = s2 * np.linalg.inv(J.T @ J)
    return x, r, cov


def fit(tp3_path, tp4_path, out_prefix="tbk_tst_001", quiet=False):
    tp3, tp4 = read_log(tp3_path), read_log(tp4_path)
    t, d, t_tp3_end = join(tp3, tp4)
    T0 = float(np.nanmean([d["T3_C"][0], d["T4_C"][0]]))   # sand only; T1 carries the heater offset
    print(f"record: {t[-1] / 3600:.1f} h ({t_tp3_end / 3600:.1f} h charge), start {T0:.0f} C uniform")

    r0, sim0 = residuals(Params().x(), t, d, T0)
    rms0 = sqrt(float(r0 @ r0) / len(r0))
    print(f"unfitted model (TBK-CAL-002 values): RMS {rms0:.2f} K")

    lo, hi = np.log([0.3, 0.1, 0.3, 0.8]), np.log([3.0, 10.0, 3.0, 1.25])
    x, r, cov = levenberg_marquardt(lambda xx: residuals(xx, t, d, T0), Params().x(), lo, hi)
    p = Params.from_x(x)
    sx = np.sqrt(np.diag(cov))
    ci = {n: [float(np.exp(x[i] - 1.96 * sx[i])), float(np.exp(x[i] + 1.96 * sx[i]))] for i, n in enumerate(Params.names)}
    ci["h_contact"] = [v * H_CONTACT_0 for v in ci["h_contact"]]
    rms = sqrt(float(r @ r) / len(r))
    _, sim = residuals(x, t, d, T0)

    # Per-channel RMS
    idx = np.arange(0, len(t), 6)
    rms_ch = {}
    for ch, key in (("T1_C", "T1"), ("T4_C", "T4"), ("T3_C", "T3")):
        e = d[ch][idx] - np.interp(t[idx], sim["t"], sim[key])
        rms_ch[key] = float(np.sqrt(np.nanmean(e ** 2)))

    # Energy balance over TP3 from measured temperatures (independent of the model state)
    in_tp3 = t <= t_tp3_end
    P = np.nan_to_num(d["heater_W"])
    E_in = p.p_scale * float(np.trapezoid(P[in_tp3], t[in_tp3]))   # corrected heater energy
    E_meas = measured_energy_j(d["T1_C"], d["T4_C"], d["T3_C"])
    Tl, Ql = loss_table(p.k_ins)
    k_end = int(np.where(in_tp3)[0][-1])
    loss_t = np.interp(np.interp(t, sim["t"], sim["Tmean"]), Tl, Ql)
    E_loss = float(np.trapezoid(loss_t[in_tp3], t[in_tp3]))
    dE = E_meas[k_end] - E_meas[0]
    closure = (E_in - dE - E_loss) / E_in

    # Time to 80 % charge. Measured: the energy balance, corrected heater energy less the loss
    # fitted on the cool-down, added to the heat at the start. Predicted: a run of the fitted
    # model under its own 550 C well-wall controller. The comparison tests whether the real
    # controller and bed take heat as fast as the model says.
    e_lo = RHO * float(h_of(T_LO)) * D["sand_vol_m3"]
    e_hi = RHO * float(h_of(T_HI)) * D["sand_vol_m3"]
    e80 = e_lo + 0.8 * (e_hi - e_lo)
    e0 = RHO * float(h_of(T0)) * D["sand_vol_m3"]
    tt = t[in_tp3]
    net = p.p_scale * P[in_tp3] - loss_t[in_tp3]
    e_bal = e0 + np.concatenate([[0.0], np.cumsum(0.5 * (net[1:] + net[:-1]) * np.diff(tt))])
    hit = np.where(e_bal >= e80)[0]
    t80_meas = float(tt[hit[0]]) if len(hit) else float("nan")
    pred = simulate(p, t, P, T0, controller=True, t_end=24 * 3600)
    hitp = np.where(pred["E"] >= e80)[0]
    t80_pred = float(pred["t"][hitp[0]]) if len(hitp) else float("nan")
    t80_err = (t80_pred - t80_meas) / t80_meas if t80_meas == t80_meas else float("nan")

    # Well-wall limit reached (first sub-100 % duty on the heaters)
    full = TA["heater_w"] * N_HEAT
    below = np.where(P[in_tp3] < 0.98 * full)[0]
    below = below[below > 5]
    t_limit = float(t[in_tp3][below[0]]) if len(below) else float("nan")

    # TP4: loss at 450, 300 and 150 C from the fitted envelope
    loss_fit = {int(T): float(np.interp(T, Tl, Ql)) for T in (450, 300, 150)}
    loss_pred = float(ta.standby(450.0)["total"])
    loss_err = (loss_fit[450] - loss_pred) / loss_pred

    result = {
        "files": {"tp3": str(tp3_path), "tp4": str(tp4_path)},
        "start_T_C": T0,
        "params": p.as_dict(),
        "ci95": ci,
        "rms_K": {"fitted": rms, "unfitted": rms0, **{f"fitted_{k}": v for k, v in rms_ch.items()}},
        "energy_balance_tp3": {"heater_kWh": E_in / 3.6e6, "stored_from_temps_kWh": dE / 3.6e6,
                               "loss_kWh": E_loss / 3.6e6, "closure": closure},
        "t80_h": {"measured": t80_meas / 3600, "predicted": t80_pred / 3600, "error": t80_err},
        "t_wall_limit_h": t_limit / 3600,
        "loss_W": {"fitted_at_450": loss_fit[450], "fitted_at_300": loss_fit[300],
                   "fitted_at_150": loss_fit[150], "predicted_at_450": loss_pred, "error": loss_err},
        "pass": {
            "TP3_rms_le_10K": bool(rms <= 10.0),
            "TP3_t80_within_10pct": bool(abs(t80_err) <= 0.10) if t80_err == t80_err else False,
            "TP4_loss_within_20pct": bool(abs(loss_err) <= 0.20),
            "energy_closure_within_10pct": bool(abs(closure) <= 0.10),
            "power_correction_within_5pct": bool(abs(p.p_scale - 1) <= 0.05),
        },
    }
    RESULTS.mkdir(exist_ok=True)
    jpath = RESULTS / f"{out_prefix}_fit.json"
    jpath.write_text(json.dumps(result, indent=2) + "\n")
    figure(t, d, sim, RESULTS / f"{out_prefix}_fit.svg", t_tp3_end)
    if not quiet:
        report(result)
    print(f"wrote {jpath.relative_to(ROOT)} and {jpath.with_suffix('.svg').name}")
    return result


def report(res):
    p, ci = res["params"], res["ci95"]
    print("\nFitted parameters (95 % interval from the Jacobian; optimistic, since residuals are correlated)")
    print(f"  sand conductivity multiplier  {p['k_sand']:.3f}  [{ci['k_sand'][0]:.3f}, {ci['k_sand'][1]:.3f}]")
    print(f"  wall contact conductance      {p['h_contact']:.0f} W/(m2 K)  [{ci['h_contact'][0]:.0f}, {ci['h_contact'][1]:.0f}]")
    print(f"  insulation multiplier         {p['k_ins']:.3f}  [{ci['k_ins'][0]:.3f}, {ci['k_ins'][1]:.3f}]")
    print(f"  heater power correction       {p['p_scale']:.3f}  [{ci['p_scale'][0]:.3f}, {ci['p_scale'][1]:.3f}]")
    r = res["rms_K"]
    print(f"RMS: unfitted {r['unfitted']:.2f} K, fitted {r['fitted']:.2f} K "
          f"(T1 {r['fitted_T1']:.2f}, T4 {r['fitted_T4']:.2f}, T3 {r['fitted_T3']:.2f})")
    e = res["energy_balance_tp3"]
    print(f"TP3 energy: heater {e['heater_kWh']:.2f} kWh = stored {e['stored_from_temps_kWh']:.2f} + loss "
          f"{e['loss_kWh']:.2f}; closure {e['closure'] * 100:+.1f} %")
    t80 = res["t80_h"]
    print(f"TP3 time to 80 %: measured {t80['measured']:.2f} h, predicted {t80['predicted']:.2f} h "
          f"({t80['error'] * 100:+.1f} %); well-wall limit reached at {res['t_wall_limit_h']:.2f} h")
    lw = res["loss_W"]
    print(f"TP4 loss: fitted {lw['fitted_at_450']:.0f} W at 450 C against {lw['predicted_at_450']:.0f} W predicted "
          f"({lw['error'] * 100:+.1f} %); {lw['fitted_at_300']:.0f} W at 300 C, {lw['fitted_at_150']:.0f} W at 150 C")
    print("Pass: " + ", ".join(f"{k} {'PASS' if v else 'FAIL'}" for k, v in res["pass"].items()))


def figure(t, d, sim, path, t_split):
    h = t / 3600
    hs = sim["t"] / 3600
    step = max(1, len(h) // 400)
    series_l = [(list(h[::step]), list(np.nan_to_num(d["heater_W"][::step]) / 1000), "Heater power (kW)", False, 0.1)]
    series_r = []
    split = float(t_split / t[-1])
    for ch, key, frac in (("T1_C", "T1", 0.5 * split), ("T4_C", "T4", 0.8 * split), ("T3_C", "T3", 0.6)):
        m = d[ch][::step]
        ok = ~np.isnan(m)
        series_r.append((list(h[::step][ok]), list(m[ok]), "", True, frac))
        series_r.append((list(hs), list(sim[key]), key, False, frac))
    base.svg_chart(path, "TP3 and TP4: measured (dashed) against fitted model (solid)", "Time (h)",
                   float(np.ceil(h[-1] / 4) * 4), series_l, series_r, "Power (kW)", (0, 1.2),
                   "Temperature (°C)", (0, 600))


# ---------------------------------------------------------------- TP5 prediction
def discharge_model(p: Params, t, airflow, t_in, T0, dt_s=60.0):
    """Exchanger duty (W) of the U-tube over a record, driven by the logged airflow (L/s)
    and inlet air temperature, with standby loss. One leg cell, as in TBK-CAL-002 section 4."""
    Tl, Ql = loss_table(p.k_ins)
    n_legs = 2 * TA["n_utubes"]
    r1 = TA["tube_od"] / 2000
    r2 = sqrt((D["sand_area_m2"] / n_legs + pi * r1 ** 2) / pi)
    L_cell = 2 * D["sand_depth_eq"] / 1000
    bed = Bed(p, T0, r1=r1, r2=r2)
    tk, times, model_q = 0.0, [], []
    while tk <= t[-1]:
        v = float(np.interp(tk, t, airflow))
        Tin = float(np.interp(tk, t, t_in))
        loss = float(np.interp(bed.mean(), Tl, Ql))
        Q = 0.0
        if v > 0:
            m = v / 1000 * base.air(Tin)[0] / TA["n_utubes"]
            Tw = bed.T[0]
            for _ in range(3):
                _, Qt, _, _, _ = base.utube_air(m, Tw)
                Tw = bed.t_wall(-Qt / L_cell)
            Q = TA["n_utubes"] * Qt
        times.append(tk)
        model_q.append(Q)
        bed.step(-Q / TA["n_utubes"] / L_cell, loss / (n_legs * L_cell / 2), dt_s)
        tk += dt_s
    return np.array(times), np.array(model_q)


def tp5(tp5_path, params_path, out_name="tbk_tst_001_tp5.json"):
    fitted = json.loads(Path(params_path).read_text())["params"]
    p = Params(**fitted)
    s0, t, d = read_log(tp5_path)
    T0 = float(np.nanmean([d["T3_C"][0], d["T4_C"][0]]))
    times, model_q = discharge_model(p, t, np.nan_to_num(d["airflow_Ls"]), np.nan_to_num(d["T6_C"], nan=20.0), T0)
    meas = d["exchanger_W"]
    rows = []
    for hr in range(1, int(t[-1] // 3600) + 1):    # hourly means; the first hour is settling
        sel = (t >= (hr - 1) * 3600) & (t < hr * 3600)
        selm = (times >= (hr - 1) * 3600) & (times < hr * 3600)
        qm, qp = float(np.nanmean(meas[sel])), float(np.mean(model_q[selm]))
        err = (qp - qm) / qm if qm > 5 else float("nan")
        rows.append({"hour": hr, "measured_W": qm, "model_W": qp, "error": err, "scored": hr > 1})
        print(f"  hour {hr:2d}: measured {qm:6.1f} W  model {qp:6.1f} W  {err * 100:+6.1f} %"
              + ("" if hr > 1 else "  (settling, not scored)"))
    scored = [r["error"] for r in rows if r["scored"] and r["error"] == r["error"]]
    ok = bool(scored) and bool(all(abs(e) <= 0.15 for e in scored))
    print(f"TP5 hourly duty within 15 %: {'PASS' if ok else 'FAIL'} ({len(scored)} hours scored)")
    note = ("Starts from a uniform bed at the mean of T3 and T4. The bed is not uniform after a "
            "charge, which is why the first hour is not scored.")
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / out_name
    out.write_text(json.dumps({"file": str(tp5_path), "params": fitted, "hours": rows, "pass": ok, "note": note},
                              indent=2) + "\n")
    print(f"wrote {out.relative_to(ROOT)}")
    return ok


# ---------------------------------------------------------------- synthetic self-test
def write_synthetic(path, start, t, P, T1, T3, T4):
    with open(path, "w", encoding="utf-8") as f:
        f.write("# synthetic record from tbk_tst_001_fit.py selftest\n")
        f.write("host_time,seq,t_s,T1_C,T3_C,T4_C,T5_C,T6_C,heater_mode,setpoint_C,heater_duty,heater_W,"
                "heater_Wh,blower_mode,blower_duty,airflow_Ls,exchanger_W,faults\n")
        for i in range(len(t)):
            ts = (start + dt.timedelta(seconds=float(t[i]))).isoformat(timespec="seconds")
            duty = P[i] / (TA["heater_w"] * N_HEAT)
            f.write(f"{ts},{i + 1},{int(t[i])},{T1[i]:.2f},{T3[i]:.2f},{T4[i]:.2f},,20.00,1,550.0,{duty:.3f},"
                    f"{P[i]:.1f},0,0,0.000,0.00,,0\n")


def selftest(seed=1):
    """Make TP3 and TP4 records from known parameters with the controller-driven model, add
    thermocouple noise and a 2 % power error, then fit and check the parameters come back."""
    rng = np.random.default_rng(seed)
    true = Params(k_sand=0.85, h_contact=220.0, k_ins=1.15)
    T0 = 150.0
    charge = simulate(true, None, None, T0, dt=30.0, controller=True, t_end=15 * 3600)
    # cool-down from the end state of the charge
    Tl, Ql = loss_table(true.k_ins)
    bed = Bed(true, T0)
    q_hist = charge["P"] / (N_HEAT * L_EQ)
    for q in q_hist:
        bed.step(q, float(np.interp(bed.mean(), Tl, Ql)) / (N_HEAT * L_EQ), 30.0)
    cool = {k: [] for k in ("t", "T1", "T3", "T4")}
    for k in range(int(48 * 3600 / 30)):
        cool["t"].append(k * 30.0)
        cool["T1"].append(bed.t_wall(0.0))
        cool["T3"].append(float(bed.T[-1]))
        cool["T4"].append(bed.t_at(R_T4))
        bed.step(0.0, float(np.interp(bed.mean(), Tl, Ql)) / (N_HEAT * L_EQ), 30.0)

    out = RESULTS / "selftest"
    out.mkdir(parents=True, exist_ok=True)
    start = dt.datetime(2026, 1, 1, 8, 0, tzinfo=dt.timezone.utc)
    t3 = np.arange(0, charge["t"][-1], 10.0)
    noise = lambda n: rng.normal(0, 1.5, n)  # noqa: E731
    P3 = np.interp(t3, charge["t"], charge["P"]) * 1.02          # logged power reads 2 % high
    write_synthetic(out / "synthetic_TP3.csv", start, t3, P3,
                    np.interp(t3, charge["t"], charge["T1"]) + noise(len(t3)),
                    np.interp(t3, charge["t"], charge["T3"]) + noise(len(t3)),
                    np.interp(t3, charge["t"], charge["T4"]) + noise(len(t3)))
    t4 = np.arange(0, cool["t"][-1], 10.0)
    start4 = start + dt.timedelta(seconds=float(t3[-1] + 10))
    write_synthetic(out / "synthetic_TP4.csv", start4, t4, np.zeros(len(t4)),
                    np.interp(t4, cool["t"], cool["T1"]) + noise(len(t4)),
                    np.interp(t4, cool["t"], cool["T3"]) + noise(len(t4)),
                    np.interp(t4, cool["t"], cool["T4"]) + noise(len(t4)))
    print(f"synthetic truth: k_sand {true.k_sand}, h_contact {true.h_contact}, k_ins {true.k_ins}")
    res = fit(out / "synthetic_TP3.csv", out / "synthetic_TP4.csv", out_prefix="selftest/selftest")
    got = res["params"]
    checks = {
        "k_sand within 5 %": abs(got["k_sand"] / true.k_sand - 1) <= 0.05,
        "h_contact within 30 %": abs(got["h_contact"] / true.h_contact - 1) <= 0.30,
        "k_ins within 5 %": abs(got["k_ins"] / true.k_ins - 1) <= 0.05,
        "p_scale within 2 % (logged power reads 2 % high)": abs(got["p_scale"] * 1.02 - 1) <= 0.02,
        "fitted RMS near noise (under 2.5 K)": res["rms_K"]["fitted"] < 2.5,
    }
    # TP5: a stepped-airflow discharge made with the true parameters, predicted with the fitted ones
    t5 = np.arange(0, 20 * 3600, 10.0)
    air5 = np.where(t5 < 8 * 3600, 1.0, np.where(t5 < 16 * 3600, 2.0, 4.0))
    tq, q5 = discharge_model(true, t5, air5, np.full(len(t5), 20.0), 420.0)
    q5 = np.interp(t5, tq, q5) * (1 + rng.normal(0, 0.03, len(t5)))
    with open(out / "synthetic_TP5.csv", "w", encoding="utf-8") as f:
        f.write("host_time,seq,t_s,T1_C,T3_C,T4_C,T5_C,T6_C,heater_mode,setpoint_C,heater_duty,heater_W,"
                "heater_Wh,blower_mode,blower_duty,airflow_Ls,exchanger_W,faults\n")
        for i in range(len(t5)):
            ts = (start + dt.timedelta(seconds=float(t5[i]))).isoformat(timespec="seconds")
            f.write(f"{ts},{i + 1},{int(t5[i])},,420.00,420.00,,20.00,0,550.0,0,0,0,1,0.5,{air5[i]:.2f},{q5[i]:.1f},0\n")
    checks["TP5 prediction within 15 %"] = tp5(out / "synthetic_TP5.csv", RESULTS / "selftest" / "selftest_fit.json",
                                              out_name="selftest/selftest_tp5.json")
    for k, v in checks.items():
        print(f"  {k}: {'ok' if v else 'FAILED'}")
    ok = bool(all(checks.values()))
    print("selftest " + ("PASSED" if ok else "FAILED"))
    return ok


def main():
    ap = argparse.ArgumentParser(description="TBK-TST-001 analysis")
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fit", help="fit TP3 and TP4")
    f.add_argument("--tp3", required=True)
    f.add_argument("--tp4", required=True)
    p5 = sub.add_parser("tp5", help="predict TP5 with fitted parameters")
    p5.add_argument("--tp5", required=True)
    p5.add_argument("--params", default=str(RESULTS / "tbk_tst_001_fit.json"))
    st = sub.add_parser("selftest", help="recover known parameters from synthetic data")
    st.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    if a.cmd == "fit":
        fit(Path(a.tp3), Path(a.tp4))
    elif a.cmd == "tp5":
        sys.exit(0 if tp5(Path(a.tp5), a.params) else 1)
    else:
        sys.exit(0 if selftest(a.seed) else 1)


if __name__ == "__main__":
    main()
