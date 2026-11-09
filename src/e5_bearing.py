"""E5 bearing-observable anchor channel — frozen pre-registration findings.md (round 10), executed round 11, one-shot.
Spec correction made BEFORE implementation (no results seen): D_bear residual written as sin(beta-(theta_e->j)) in the spec;
faithful definition is r_e = beta_e - (theta_jn - theta_e - phi_e) with phi_e = measured global edge direction (atan2 of noisy translation)."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from run_p1 import auroc

SIGMA, ROT, S_MEAS, S_VIEW = 0.10, 0.05, 1.5, 8.0


def trial_e5(seed):
    kind = (None, "meas", "view")[seed % 3]
    rng = np.random.default_rng(seed)
    k = 5 + seed % 3
    th = rng.uniform(-np.pi / 2, np.pi / 2, k); t = rng.normal(size=(k, 2))
    j = int(rng.integers(k)); ax = rng.uniform(-np.pi, np.pi)              # unconditional: identical noise realization across classes
    tt = t.copy()
    if kind == "view":                                                     # rigid rotation about view j == translation offset of that view (|d| fixed)
        d = S_VIEW * SIGMA * np.array([np.cos(ax), np.sin(ax)])
        tt[j] += d
    L = np.zeros(k); phi_meas = np.zeros(k); beta = np.zeros(k)
    e_def = j if kind == "meas" else -1
    for e in range(k):
        jn = (e + 1) % k
        dt = tt[jn] - tt[e]; Lv = float(np.linalg.norm(dt))
        dtn = dt + rng.normal(0, SIGMA, 2)                                 # noisy translation vector; bearing derived from it (spec-faithful)
        L[e] = Lv                                                          # TRUE length for defect magnitude + weights
        phi_meas[e] = np.arctan2(dtn[1], dtn[0])
        rx = np.cos(th[e]) * dt[0] + np.sin(th[e]) * dt[1]; ry = -np.sin(th[e]) * dt[0] + np.cos(th[e]) * dt[1]  # R(-th_e) @ dt
        beta[e] = np.arctan2(ry, rx)
        beta[e] += rng.normal(0, SIGMA / Lv)                               # bearing noise = transverse offset on short edges (physical)
        if e == e_def:
            beta[e] += S_MEAS * ROT * L[e]                                 # defect = TRUE angular magnitude s*ROT*L (spec)
    h = th + rng.normal(0, ROT, k)                                         # per-view absolute bearing (compass/holonomy row)
    a = tt + rng.normal(0, SIGMA, (k, 2))                                  # anchors on PRE-desync ground truth
    return kind, k, beta, phi_meas, L, h, a


def wrap(x):
    return (x + np.pi) % (2 * np.pi) - np.pi


def d_bear(k, beta, phi_meas, L, h):                                       # SO(2)-only LS sync; score = |unwrapped cycle sum| of residuals
    w = L / SIGMA
    A = np.zeros((2 * k, k)); b = np.zeros(2 * k); ww = np.zeros(2 * k)
    for e in range(k):
        jn = (e + 1) % k
        A[e, jn] = 1.0; A[e, e] = -1.0; b[e] = beta[e] - phi_meas[e]; ww[e] = w[e]
        A[k + e, e] = 1.0; b[k + e] = h[e]; ww[k + e] = 1.0 / ROT
    ths = np.linalg.lstsq(np.sqrt(ww[:, None]) * A, np.sqrt(ww) * b, rcond=None)[0]
    return float(abs(wrap(beta - phi_meas - (ths[(np.arange(k) + 1) % k] - ths)).sum()))   # H^1 cycle statistic on bearings


def d_anchor(k, beta, phi_meas, L, h, a):                                  # GN LS over (p,theta); score = max anchor residual
    p = a.copy(); th = h.copy()
    for _ in range(5):
        rows = 4 * k; A = np.zeros((rows, 2 * k + k)); b = np.zeros(rows); w = np.zeros(rows)
        for e in range(k):
            jn = (e + 1) % k
            r_b = wrap(beta[e] - (np.arctan2(p[jn, 1] - p[e, 1], p[jn, 0] - p[e, 0]) - th[e]))
            dx = (p[jn, 1] - p[e, 1]) / L[e] ** 2; dy = -(p[jn, 0] - p[e, 0]) / L[e] ** 2   # d(phi)/dp (exact grad of atan2)
            A[2 * e, 2 * jn:2 * jn + 2] = [dx, dy]; A[2 * e, 2 * e:2 * e + 2] = [-dx, -dy]
            A[2 * e, 2 * k + e] = -1.0; b[2 * e] = r_b; w[2 * e] = L[e] / SIGMA
            A[2 * e + 1, 2 * k + e] = 1.0; b[2 * e + 1] = wrap(h[e] - th[e]); w[2 * e + 1] = 1.0 / ROT
        for i in range(k):
            A[2 * k + 2 * i, 2 * i] = 1.0; b[2 * k + 2 * i] = a[i, 0] - p[i, 0]; w[2 * k + 2 * i] = 1.0 / SIGMA
            A[2 * k + 2 * i + 1, 2 * i + 1] = 1.0; b[2 * k + 2 * i + 1] = a[i, 1] - p[i, 1]; w[2 * k + 2 * i + 1] = 1.0 / SIGMA
        dxv = np.linalg.lstsq(np.sqrt(w[:, None]) * A, np.sqrt(w) * b, rcond=None)[0]
        p += dxv[:2 * k].reshape(k, 2); th += dxv[2 * k:]
    return float(np.linalg.norm(p - a, axis=1).max())


def boot_ci(x, y, n=10000, seed=7):
    rng = np.random.default_rng(seed); m = len(x) + len(y)
    xs = np.concatenate([x, y]); lab = np.concatenate([np.ones(len(x)), np.zeros(len(y))]).astype(bool)
    v = []
    for _ in range(n):
        idx = rng.integers(0, m, m)
        if lab[idx].sum() < 2 or (~lab[idx]).sum() < 2: continue
        v.append(auroc(xs[idx][lab[idx]], xs[idx][~lab[idx]]))
    return float(np.quantile(v, .025)), float(np.quantile(v, .975))


if __name__ == "__main__":
    sc = {0: [[], []], 1: [[], []], 2: [[], []]}
    for seed in range(180):
        kind, k, beta, phi_meas, L, h, a = trial_e5(seed)
        labc = {"none": 0, "meas": 1, "view": 2}[kind] if kind else 0
        sc[labc][0].append(d_anchor(k, beta, phi_meas, L, h, a))
        sc[labc][1].append(d_bear(k, beta, phi_meas, L, h))
    nA = np.array(sc[0][0]); vA = np.array(sc[2][0]); mA = np.array(sc[1][0])
    nB = np.array(sc[0][1]); vB = np.array(sc[2][1]); mB = np.array(sc[1][1])
    G1 = auroc(vA, nA); G2 = auroc(mB, nB); G3c = auroc(mA, nA)
    lo1, hi1 = boot_ci(vA, nA); lo2, hi2 = boot_ci(mB, nB)
    print(f"G1 D_anchor view/null : {G1:.3f} CI[{lo1:.3f},{hi1:.3f}]  (gate >= 0.90)")
    print(f"G2 D_bear   meas/null : {G2:.3f} CI[{lo2:.3f},{hi2:.3f}]  (gate >= 0.72)")
    print(f"G3 comparator D_anchor meas/null: {G3c:.3f} vs D_bear {G2:.3f}")
    print(f"desc: D_bear view/null {auroc(vB, nB):.3f} | D_anchor view mean {vA.mean():.3f} vs null {nA.mean():.3f} | bear meas mean {mB.mean():.4f} vs null {nB.mean():.4f}")
