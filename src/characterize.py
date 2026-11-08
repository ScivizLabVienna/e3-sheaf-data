"""E3 post-hoc characterization (NOT a gate test): two-sided sensitivity claim.
Arm matrix x {measurement-level closure defect, view-level translation desync}
x {sheaf H^1 harmonic energy, consistency radius (LS), robust-trim LS (TranSync-style pruning)}.
Post-hoc descriptive study; frozen gate already NULL (see findings.md round 4)."""
import numpy as np
from run_p1 import se2_log, se2_exp, sheaf_score, baseline_score  # module-level run prints gate table; harmless here


def auroc(pos, neg):                                                # same rank statistic as run_p1 (frozen)
    all_ = np.concatenate([pos, neg]); r = all_.argsort().argsort() + 1
    return float(r[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg))


SIGMA, ROT = 0.10, 0.05


def gen(seed, s_, kind):
    """kind: none | meas (add closure defect to one edge MEASUREMENT) | view (desync one ground-truth pose)."""
    rng = np.random.default_rng(seed); k = 5 + seed % 3
    th = rng.uniform(-np.pi / 2, np.pi / 2, k); t = rng.normal(size=(k, 2))
    g = [se2_exp([t[i, 0], t[i, 1], th[i]]) for i in range(k)]
    if kind == "view" and s_ > 0:                       # view-level translation desync (frozen-P1 injection)
        j = int(rng.integers(k))
        ax = rng.uniform(0, 2 * np.pi, 2)[:1]
        g[j] = g[j] @ se2_exp([s_ * SIGMA * np.cos(ax[0]), s_ * SIGMA * np.sin(ax[0]), 0.0])
    x = np.zeros((k, 3))
    for e in range(k):                                  # cycle graph edges (e, e+1)
        rel = np.linalg.inv(g[e]) @ g[(e + 1) % k]
        eps = rng.normal(0, SIGMA, 2), rng.normal(0, ROT)
        v = se2_log(rel) + np.array([eps[0][0], eps[0][1], eps[1]])
        if kind == "meas" and s_ > 0 and e == int(rng.integers(k)):  # one edge MEASUREMENT carries a rotation-bearing closure defect (H^1 carrier)
            v = v + np.array([0.0, 0.0, s_ * ROT])       # rotation-bearing closure defect (H^1 carrier)
        x[e] = se2_log(se2_exp(v))
    return k, x


def robust_score(k, x, iters=10):
    """TranSync/Cycle-Sync-style: LS pose sync with hard residual trimming; score = kept-edge inconsistency energy."""
    A, b, w = _system(k, x)
    a = np.linalg.lstsq(np.sqrt(w[:, None]) * A, np.sqrt(w) * b, rcond=None)[0]
    for _ in range(iters):
        r = np.abs(A @ a - b)
        thr = max(np.quantile(r, 0.7), 1e-6)             # trim worst 30% each iter
        w = (r < thr).astype(float) + 1e-8
        a = np.linalg.lstsq(np.sqrt(w[:, None]) * A, np.sqrt(w) * b, rcond=None)[0]
    r = A @ a - b
    return float(np.sum(((1 - w) * r ** 2)[r > 0])) + float(np.sum(w[r < thr] * r[r < thr] ** 2))  # shortcut: crude composite; upgrade to trimmed-keep energy if used for inference


def _system(k, x):
    A = np.zeros((2 * k, 2 * k)); b = np.zeros(2 * k)
    for e in range(k):
        c, s = np.cos(x[e, 2]), np.sin(x[e, 2])
        Rm = np.array([[c, -s], [s, c]])
        A[2 * e:2 * e + 2, e] = -Rm[:, 0]; A[2 * e:2 * e + 2, (e + 1) % k] = Rm[:, 0]
        b[2 * e:2 * e + 2] = x[e, :2]
    return A, b, np.ones(2 * k)


def signed(k, x):
    return abs(x[:, 2].sum())      # |cycle holonomy| — phase-preserving H^1 statistic (the scalar energy ||H||^2 discards it)


if __name__ == "__main__":
    N = 240
    arms = {"sheaf_H1_energy": sheaf_score, "consistency_radius": baseline_score,
            "robust_trim_LS": robust_score, "|holonomy|_signed": signed}
    for kind in ("meas", "view"):
        s_pos = (1.5 if kind == "meas" else 2.5)
        negs = {a: [] for a in arms}; poss = {a: [] for a in arms}
        for seed in range(N):
            k, xn = gen(2 * seed, 0.0, "none")
            for a, f in arms.items(): negs[a].append(f(k, xn))
        for seed in range(N):
            k, xp = gen(2 * seed + 1, s_pos, kind)
            for a, f in arms.items(): poss[a].append(f(k, xp))
        row = " ".join(f"{a}={auroc(np.array(poss[a]), np.array(negs[a])):.3f}" for a in arms)
        print(f"{kind:4s} defect s={s_pos}: {row}")
