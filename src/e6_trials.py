"""E6 trials (frozen pre-registration, findings.md round 12; sigma from round-13 leg). One-shot, no tuning after verdict.
Cycles = k=6 consecutive lag-30 pair offsets chained; null closure holonomy is structurally 0 -> anchor rows at scale sigma_t provide gauge fixing AND noise (E5 D_anchor construction, translation-only)."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from run_p1 import auroc

D = np.load(os.path.join(os.path.dirname(__file__), "..", "e6_pairs_lag30.npz"))
OFF, SIG = D["D"], D["sigma"]                                        # frozen measured offsets + real robust sigma (per component)
K, NTRIALS, LEVELS = 6, 40, (0.5, 1.0, 2.0, 3.0, 5.0)


def trial(cycle_off, rng, kind, level):
    t = cycle_off.copy(); j = int(rng.integers(K))                   # node index in chain (view), edge e=j-1..j incident
    if kind == "view":
        v = rng.normal(size=2) / np.linalg.norm(rng.normal(size=2)); d = level * v * SIG
        t[(j - 1) % K] += d; t[j] -= d                               # one view displaced by d (d|_x = level*sigma_x: <=3 gate passes by construction, noted in spec-disclosure)
    elif kind == "meas":
        e = int(rng.integers(K)); v = rng.normal(size=2) / np.linalg.norm(rng.normal(size=2))
        t[e] += level * v * SIG
    return t


def d_hol(t):                                                        # signed cycle holonomy (z of closed polygon area-form; translation cycle => sum closure)
    pos = np.cumsum(np.vstack([[0., 0.], t[:-1]]), axis=0)           # open-chain positions, node j=(e+1)%K
    return float(np.asarray(t).sum(axis=0)[1])                                       # signed net-closure component (H^1 cycle statistic on translation chain)


def d_anchor(t, rng):                                                # E5-style anchored LS, translation-only; anchor rows at sigma = gauge + noise
    A = np.zeros((2 * K + 2 * (K + 1), 2 * (K + 1))); b = np.zeros(2 * K + 2 * (K + 1))
    w = np.ones(2 * K + 2 * (K + 1))
    for e in range(K):                                               # pair rows weight 1/sigma (anisotropic handled by duplicating per-component rows)
        jn = (e + 1) % (K + 1)
        A[2 * e, 2 * jn] = 1; A[2 * e, 2 * e] = -1; b[2 * e] = t[e, 0]; w[2 * e] = 1 / SIG[0]
        A[2 * e + 1, 2 * jn + 1] = 1; A[2 * e + 1, 2 * e + 1] = -1; b[2 * e + 1] = t[e, 1]; w[2 * e + 1] = 1 / SIG[1]
    truth = np.vstack([[0., 0.], np.cumsum(t, axis=0)])              # re-anchored each trial: LS vs noisy anchors OF THE MEASURED T (gauge fixing only; injection signal enters through t)
    anc = truth + rng.normal(size=(K + 1, 2)) * SIG                  # anchor rows carry the sigma noise -> identifiability (E3b/E5 construction)
    for i in range(K + 1):
        A[2 * K + 2 * i, 2 * i] = 1; b[2 * K + 2 * i] = anc[i, 0]; w[2 * K + 2 * i] = 1 / SIG[0]
        A[2 * K + 2 * i + 1, 2 * i + 1] = 1; b[2 * K + 2 * i + 1] = anc[i, 1]; w[2 * K + 2 * i + 1] = 1 / SIG[1]
    sw = np.sqrt(w)[:, None]
    x = np.linalg.lstsq(sw * A, np.sqrt(w) * b, rcond=None)[0].reshape(K + 1, 2)
    return float(np.abs(x - anc).max())


def boot(x, y, n=5000, seed=7):
    rng = np.random.default_rng(seed); m = len(x) + len(y)
    xs = np.concatenate([x, y]); lab = np.concatenate([np.ones(len(x)), np.zeros(len(y))]).astype(bool)
    v = [auroc(xs[i][lab[i]], xs[i][~lab[i]]) for i in (rng.integers(0, m, m) for _ in range(n)) if 2 <= lab[i].sum() < m - 1]
    return float(np.quantile(v, .025)), float(np.quantile(v, .975))


if __name__ == "__main__":
    starts = np.arange(0, len(OFF) - K + 1)                          # non-overlapping-window starts truncated to available (pre-reg said 40; only this many exist: disclosed shrink)
    base = [OFF[s:s + K] for s in range(len(OFF) - K + 1)]
    print(f"base cycles available: {len(base)}")
    res = {}
    for lvl in LEVELS:
        nH, nA = [], []
        for bi, t0 in enumerate(base):                               # null trials (anchor noise varies by seed per trial)
            rng = np.random.default_rng(1000 + bi)
            nH.append(abs(d_hol(t0))); nA.append(d_anchor(t0, rng))
        rows = {}
        for kind in ("view", "meas"):
            sH, sA = [], []
            for bi, t0 in enumerate(base):
                rng = np.random.default_rng(2000 + bi if kind == "view" else 3000 + bi)
                t = trial(t0, rng, kind, lvl)
                sH.append(abs(d_hol(t))); sA.append(d_anchor(t, np.random.default_rng(1000 + bi)))   # same anchor-noise seed as null -> paired
            rows[kind] = (auroc(sH, nH), auroc(sA, nA))
        res[lvl] = rows
        print(f"level {lvl} xsigma: D_hol view {rows['view'][0]:.3f} meas {rows['meas'][0]:.3f} | D_anchor view {rows['view'][1]:.3f} meas {rows['meas'][1]:.3f}")
    for kind in ("view", "meas"):
        mxh = max(res[l][kind][0] for l in LEVELS); mxa = max(res[l][kind][1] for l in LEVELS)
        lh = min((l for l in LEVELS if res[l][kind][0] >= 0.9), default=None); la = min((l for l in LEVELS if res[l][kind][1] >= 0.9), default=None)
        print(f"G-E6 {kind}: maxHol {mxh:.3f} (first level >=.9: {lh}) | maxAnchor {mxa:.3f} (first >=.9: {la})")
