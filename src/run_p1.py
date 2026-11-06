"""P1 injected-desync AUROC experiment — implements the FROZEN pre-registration in findings.md verbatim. $0 cost, numpy only. Run: python src/run_p1.py"""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from sheafcore import build_deltas, harmonic_energy

def se2_log(T):  # (R|t) -> (tx, ty, th)
    return np.array([T[0, 2], T[1, 2], np.arctan2(T[1, 0], T[0, 0])])

def se2_exp(v):
    c, s, tx, ty = np.cos(v[2]), np.sin(v[2]), v[0], v[1]
    return np.array([[c, -s, tx], [s, c, ty], [0., 0., 1.]])

def wrap(a):
    return (a + np.pi) % (2 * np.pi) - np.pi

def trial(seed):
    rng = np.random.default_rng(seed)
    k = 5 + seed % 3                                                  # k in {5,6,7} rotating by seed%3
    s = 0.0 if seed % 2 == 0 else (1.5 if (seed // 2) % 2 == 0 else 2.5)  # 120 null/120 pos; alternating s within positives per pre-reg
    th = rng.uniform(-np.pi / 2, np.pi / 2, k); t = rng.normal(size=(k, 2))
    g = [se2_exp([t[i, 0], t[i, 1], th[i]]) for i in range(k)]
    if s > 0:                                                         # view-level desync: offset ONE true pose, then all its measurements recomputed
        j = rng.integers(k)
        axis = rng.uniform(-np.pi, np.pi)                             # direction of the s*sigma translation offset (free choice; recorded here)
        off = se2_exp([s * 0.10 * np.cos(axis), s * 0.10 * np.sin(axis), 0.0])
        g[j] = off @ g[j]
    E = [(i, (i + 1) % k) for i in range(k)]                          # cycle C_k pose graph
    x = np.zeros((k, 3))
    for e, (i, j) in enumerate(E):
        rel = np.linalg.inv(g[i]) @ g[j]
        eps = np.concatenate([rng.normal(0, 0.10, 2), [rng.normal(0, 0.05)]])  # sigma=0.10 trans, 0.05 rad rot
        x[e] = se2_log(se2_exp(se2_log(rel) + eps))
    return k, x

def sheaf_score(k, x):                                                # H^1 harmonic energy per R-channel, summed
    d0, d1 = build_deltas(list(range(k)), [(i, (i + 1) % k) for i in range(k)], [])
    return sum(harmonic_energy(x[:, c], d0, d1) for c in range(3))

def baseline_score(k, x):                                             # consistency radius: max residual after closed-form linear LS pose sync
    th = x[:, 2]; t = x[:, :2]
    A = np.zeros((k, k)); b = np.zeros(k)                             # edge e: a_e - a_{e+1} = th_e (cycle rows -> rank k-1; lstsq picks one gauge, residuals gauge-free)
    for e in range(k):
        A[e, e] = 1; A[e, (e + 1) % k] = -1; b[e] = th[e]
    a = np.linalg.lstsq(A, b, rcond=None)[0]
    w = np.maximum(np.abs(A.T @ (A @ a - b)) / k, 1e-8)   # per-node slack (cycle defect spread over cycle; peaks at desynced node)
    Wm = np.sqrt(w * w[(np.arange(k) + 1) % k])            # symmetric edge weight sqrt(w_i w_j), IVES-style
    M = np.zeros((2 * k, 2 * k)); rhs = np.zeros(2 * k)                   # translation LS: t_j - t_i = dt_e weighted (IVES/BM-style)
    v = np.zeros((2 * k, k))
    for e in range(k):
        u = np.zeros(k); u[e] = 1; u[(e + 1) % k] = -1
        M[2 * e:2 * e + 2] = Wm[e] * np.kron(u, np.eye(2)); rhs[2 * e:2 * e + 2] = Wm[e] * t[e]
    p = np.linalg.lstsq(M, rhs, rcond=None)[0].reshape(k, 2)
    res = np.empty(k)
    for e in range(k):
        i, j = e, (e + 1) % k
        res[e] = np.hypot(np.linalg.norm(x[e, :2] - (p[j] - p[i])), wrap(x[e, 2] - (a[j] - a[i])))
    return res.max()

def auroc(pos, neg):                                                  # Mann-Whitney U rank statistic
    all_ = np.concatenate([pos, neg]); r = all_.argsort().argsort() + 1
    return float(r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))

scores = {n: {"sheaf": [], "base": [], "y": None} for n in ("all", "s15", "s25")}
for seed in range(240):                                               # pre-registered: seeds 0..239, 120 pos / 120 neg
    k, x = trial(seed)
    scores["all"]["sheaf"].append(sheaf_score(k, x)); scores["all"]["base"].append(baseline_score(k, x))
    if seed % 2: scores["s15" if (seed // 2) % 2 == 0 else "s25"]["sheaf"].append(sheaf_score(k, x)) ; scores["s15" if (seed // 2) % 2 == 0 else "s25"]["base"].append(baseline_score(k, x))
out = {}
for name, d in scores.items():
    pos_s, neg_s = np.array(d["sheaf"]), np.array(d["base"])          # positives at odd seeds; nulls at even (trial() returns s per seed)
    y = np.array([seed % 2 for seed in range(240)]) if name == "all" else np.ones(len(pos_s), int)
    if name == "all":
        ps, pn = pos_s[y == 1], pos_s[y == 0]; bs, bn = neg_s[y == 1], neg_s[y == 0]
        a_s, a_b = auroc(ps, pn), auroc(bs, bn)
    else:                                                             # per-strength vs nulls
        ps, pn = pos_s, np.array(scores["all"]["sheaf"][::2]); bs, bn = neg_s, np.array(scores["all"]["base"][::2])
        a_s, a_b = auroc(ps, pn), auroc(bs, bn)
    out[name] = (a_s, a_b, a_s - a_b)
print(f"n={len(scores['all']['sheaf'])} pos+neg; k rotates 5/6/7")
for name, (a_s, a_b, dlt) in out.items():
    print(f"AUROC {name:4s}: sheaf={a_s:.3f} baseline={a_b:.3f} delta(sheaf-baseline)={dlt:+.3f}")
rng_b = np.random.default_rng(7)                                      # 2000-resample bootstrap CI on the all-trial delta
ps, pn = np.array(scores["all"]["sheaf"])[1::2], np.array(scores["all"]["sheaf"])[0::2]
bs, bn = np.array(scores["all"]["base"])[1::2], np.array(scores["all"]["base"])[0::2]
deltas = []
for _ in range(2000):
    ip, in_ = rng_b.integers(0, 120, 120), rng_b.integers(0, 120, 120)
    deltas.append(auroc(ps[ip], pn[in_]) - auroc(bs[ip], bn[in_]))
lo, hi = np.percentile(deltas, [2.5, 97.5])
print(f"delta CI95 = [{lo:+.3f}, {hi:+.3f}]  gate: survive iff delta >= +0.05 (pre-registered)")
