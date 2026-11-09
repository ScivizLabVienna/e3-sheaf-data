"""E4 two-channel QC triage — frozen pre-registration in findings.md (round 8), executed round 9, one-shot.
Classes: null / meas (rotation closure defect on ONE edge MEASUREMENT, s=1.5 x ROT) / view (translation desync ONE view, s=8 -> |d|=0.8).
Detectors verbatim: D_anchor = probe_e3b.anchor_score LS reading; D_hol = characterize.signed (edge channel only).
Generator = trial_anchored structure with class injection at the frozen P1/characterize conventions; noise realization IDENTICAL
across classes (draw j+axis unconditionally) so paired-seed triage is meaningful."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from run_p1 import se2_exp, se2_log, auroc
from probe_e3b import anchor_score
from characterize import signed


def trial_e4(seed):
    kind = (None, "meas", "view")[seed % 3]
    s_meas, s_view, SIGMA, ROT = 1.5, 8.0, 0.10, 0.05
    rng = np.random.default_rng(seed)
    k = 5 + seed % 3
    th = rng.uniform(-np.pi / 2, np.pi / 2, k); t = rng.normal(size=(k, 2))
    g = [se2_exp([t[i, 0], t[i, 1], th[i]]) for i in range(k)]
    j = int(rng.integers(k)); ax = rng.uniform(-np.pi, np.pi)              # unconditional draws: same noise realization across classes
    if kind == "view":
        d = s_view * SIGMA * np.array([np.cos(ax), np.sin(ax)])
        g[j] = se2_exp([d[0], d[1], 0.0]) @ g[j]
    x = np.zeros((k, 3))
    e_def = j if kind == "meas" else -1                                    # reuse same slot for the defect edge index (frozen characterize convention: random single edge)
    for e in range(k):
        jn = (e + 1) % k
        rel = np.linalg.inv(g[e]) @ g[jn]
        eps = np.concatenate([rng.normal(0, SIGMA, 2), [rng.normal(0, ROT)]])
        x[e] = se2_log(se2_exp(se2_log(rel) + eps))                        # P1-frozen SE(2)-additive measurement law
        if e == e_def:
            x[e, 2] += s_meas * ROT                                        # rotation-bearing closure defect (H^1 carrier)
    a = t + rng.normal(0, SIGMA, (k, 2))                                   # anchors always PRE-desync truth + noise
    return kind, k, x, a


if __name__ == "__main__":
    lab = {"none": 0, "meas": 1, "view": 2}
    y = []; zs = {1: [], 2: []}
    for seed in range(180):
        kind, k, x, a = trial_e4(seed)
        y.append(lab[str(kind)] if kind else 0)
        zs[1].append(anchor_score(k, x, a)[1])                             # D_anchor (LS reading, frozen from E3b)
        zs[2].append(signed(k, x))                                         # D_hol (frozen from characterize)
    y = np.array(y)
    z = {c: np.array(v) for c, v in zs.items()}
    null = (y == 0); meas = (y == 1); view = (y == 2)
    g1 = auroc(z[2][view], z[2][null])                                     # D_hol on view (sanity only, not gated)
    G1 = auroc(z[1][view], z[1][null]); G2 = auroc(z[1][meas], z[1][null]); G3 = auroc(z[2][meas], z[2][null])
    print(f"G1 D_anchor view/null : {G1:.3f}  (gate >= 0.90)")
    print(f"G2 D_anchor meas/null : {G2:.3f}  (gate >= 0.85; mechanism risk disclosed pre-run)")
    print(f"G3 D_hol   meas/null  : {G3:.3f}  (replication leg: 0.659 +- 0.04)")
    print(f"     D_hol view/null  : {g1:.3f}  (structural blindness expected, descriptive)")
    # triage (descriptive): null test = max-z > m_null + 3 sd_null; else argmax z-class
    zc = np.stack([z[1], z[2]], axis=1)                                    # trials x channels
    mu = zc[null].mean(0); sd = zc[null].std(0)
    zn = (zc - mu) / sd
    pred = np.where(zn.max(1) > 3.0, 1 + np.argmax(zn, axis=1), 0)
    for c, name in ((0, "null"), (1, "meas"), (2, "view")):
        row = [int(((y == c) & (pred == p)).sum()) for p in range(3)]
        print(f"triage {name:4s} recall {row[c] / max((y == c).sum(), 1):.2f}  -> pred null/meas/view {row}")
