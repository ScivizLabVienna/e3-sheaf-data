"""E3b anchor-channel feasibility probe — pre-registration in findings.md (2026-11-08 round 6), executed 2026-11-09.
Independent absolute channel = anchors observed on PRE-desync positions (arXiv:2608.06885 Prop.2 analog; SciViz GCP analog).
ONE-SHOT gate: AUROC(anchor-residual score) >= 0.85 aggregate over n=240 (120 null / 120 pos, P1-matched noise & desync model).
Detector history (both faithful readings of the pre-registration text, both frame-correct): measured-angle max-pairwise and
measured-angle gauge-anchored LS; NEITHER came near the gate -> one-shot NULL. The pre-registration fixed the score family
("anchor-vs-fit residual under gauge-free LS") but not the edge-channel frame convention when angles are noisy; BOTH readings
were computed before any verdict, and an oracle ceiling (post-hoc diagnostic, see oracle_ls) explains WHY no reading could pass."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from run_p1 import se2_exp, se2_log, auroc


def trial_anchored(seed, anchor_post=False):
    """RNG draw sequence IDENTICAL to run_p1.trial(seed) (same s/k/desync convention); adds anchors."""
    rng = np.random.default_rng(seed)
    k = 5 + seed % 3
    s = 0.0 if seed % 2 == 0 else (1.5 if (seed // 2) % 2 == 0 else 2.5)
    th = rng.uniform(-np.pi / 2, np.pi / 2, k); t = rng.normal(size=(k, 2))   # true PRE-desync translations
    g = [se2_exp([t[i, 0], t[i, 1], th[i]]) for i in range(k)]
    j = -1; d = np.zeros(2)
    if s > 0:
        j = int(rng.integers(k)); axis = rng.uniform(-np.pi, np.pi)
        d = s * 0.10 * np.array([np.cos(axis), np.sin(axis)])                  # off = se2_exp([d,0])
        g[j] = se2_exp([d[0], d[1], 0.0]) @ g[j]
    x = np.zeros((k, 3))
    truthG = np.zeros((k, 2))                                                 # per-sim ground truth: global-frame noiseless edge vectors
    for e in range(k):
        jn = (e + 1) % k
        rel = np.linalg.inv(g[e]) @ g[jn]
        eps = np.concatenate([rng.normal(0, 0.10, 2), [rng.normal(0, 0.05)]])
        truthG[e] = np.array([g[jn][0, 2] - g[e][0, 2], g[jn][1, 2] - g[e][1, 2]])  # global-frame noiseless edge vector
        x[e] = se2_log(se2_exp(se2_log(rel) + eps))
    a = t.copy() + (d if anchor_post and s > 0 else np.zeros(2)) \
        + rng.normal(0, 0.10, (k, 2))                                          # anchors LAST: N(0,.10^2 I); pre-desync unless diagnostic
    return k, x, a, j, t, truthG


def anchor_score(k, x, a):
    """Frozen statistic family -> (pairwise, ls):
    pairwise = max_e | R(theta_meas_i) @ t_obs_ij - (a_j - a_i) |
    ls       = gauge-anchored LS fit p (edge targets rotated by MEASURED angles), then max_i |p_i - a_i|."""
    c, s_ = np.cos(x[:, 2]), np.sin(x[:, 2])
    ds = []
    for e in range(k):
        jn = (e + 1) % k
        Rg = np.array([[c[e], -s_[e]], [s_[e], c[e]]])
        ds.append(np.linalg.norm(Rg @ x[e, :2] - (a[jn] - a[e])))
    pairwise = float(np.max(ds))
    A = np.zeros((4 * k, 2 * k)); b = np.zeros(4 * k)
    for e in range(k):
        jn = (e + 1) % k
        Rg = np.array([[c[e], -s_[e]], [s_[e], c[e]]])
        A[2 * e:2 * e + 2, 2 * e:2 * e + 2] = -np.eye(2); A[2 * e:2 * e + 2, 2 * jn:2 * jn + 2] = np.eye(2)
        b[2 * e:2 * e + 2] = Rg @ x[e, :2]
    for i in range(k):
        A[2 * k + i, 2 * i] = 1.0; A[3 * k + i, 2 * i + 1] = 1.0
        b[2 * k + i] = a[i, 0]; b[3 * k + i] = a[i, 1]
    p = np.linalg.lstsq(A, b, rcond=None)[0].reshape(k, 2)
    ls = float(np.abs(p - a).max())
    return pairwise, ls


def theta_true(seed):
    """TRUE per-view angles via the sim's own draw order (single-process; no hand arithmetic)."""
    rng = np.random.default_rng(seed)
    s = 0.0 if seed % 2 == 0 else (1.5 if (seed // 2) % 2 == 0 else 2.5)
    k = 5 + seed % 3
    th = rng.uniform(-np.pi / 2, np.pi / 2, k); _t = rng.normal(size=(k, 2))
    if s > 0:
        rng.integers(k); rng.uniform(-np.pi, np.pi)
    return k, th


def oracle_ls(seed, anchor_post=False):
    """DIAGNOSTIC ceiling (post-hoc, NOT the frozen statistic): TRUE per-view angles rotate the measured local obs ->
    edge channel becomes exact-truth + eps translation obs; LS pooling as in `ls`. Upper bound on ANY anchor-channel detector."""
    k, x, a, j, t, truthG = trial_anchored(seed, anchor_post)
    _, th = theta_true(seed)
    A = np.zeros((4 * k, 2 * k)); b = np.zeros(4 * k)
    for e in range(k):
        jn = (e + 1) % k
        Rg = np.array([[np.cos(th[e]), -np.sin(th[e])], [np.sin(th[e]), np.cos(th[e])]])
        A[2 * e:2 * e + 2, 2 * e:2 * e + 2] = -np.eye(2); A[2 * e:2 * e + 2, 2 * jn:2 * jn + 2] = np.eye(2)
        b[2 * e:2 * e + 2] = Rg @ x[e, :2]
    for i in range(k):
        A[2 * k + i, 2 * i] = 1.0; A[3 * k + i, 2 * i + 1] = 1.0
        b[2 * k + i] = a[i, 0]; b[3 * k + i] = a[i, 1]
    p = np.linalg.lstsq(A, b, rcond=None)[0].reshape(k, 2)
    return float(np.abs(p - a).max())


def identity_rotation_check():
    """Frame-free fixture: all true rotations ZERO => global frame == local frame, no trig audit traps.
    Builds x (edges), a (anchors), truthG directly; asserts channel consistency on null and score lift under desync."""
    k = 5
    tt = np.array([[0.0, 0.0], [2.0, 0.0], [2.0, 1.0], [0.0, 1.0], [1.0, 0.3]])   # pre-desync positions
    # NULL channel: edges and anchors agree to within 3 sigma over both channels (~0.1 each)
    rng = np.random.default_rng(7)
    x = np.zeros((k, 3))
    for e in range(k):
        xn = (e + 1) % k
        x[e] = np.concatenate([tt[xn] - tt[e] + rng.normal(0, 0.10, 2), [rng.normal(0, 0.05)]])
    a_null = tt.copy() + rng.normal(0, 0.10, (k, 2))
    s_null = anchor_score(k, x, a_null)
    # POSITIVE: view 3 desynced by d=(0.30,0.00) for edges/anchors-post; anchors (gate arm) stay PRE
    d = np.array([0.30, 0.0])
    tp = tt.copy(); tp[3] += d                                                     # post-desync positions (views used by edge measurements)
    xp = np.zeros((k, 3))
    for e in range(k):
        xn = (e + 1) % k
        xp[e] = np.concatenate([tp[xn] - tp[e] + rng.normal(0, 0.10, 2), [rng.normal(0, 0.05)]])
    a_post = tp.copy() + rng.normal(0, 0.10, (k, 2))                               # diagnostic anchors (same channel)
    a_gate = tt.copy() + rng.normal(0, 0.10, (k, 2))                               # gate anchors: PRE-desync truth + noise only
    s_gate = anchor_score(k, xp, a_gate)
    s_post = anchor_score(k, xp, a_post)
    print(f"fixture (d=0.30): null pairwise {s_null[0]:.3f} ls {s_null[1]:.3f} | PRE-anchors {s_gate[0]:.3f} {s_gate[1]:.3f} | POST-anchors {s_post[0]:.3f} {s_post[1]:.3f}")
    # theory: view 3 held by 1 anchor row + hit by 2 edge rows (equal weights) -> LS splits d; residual ~ d/3 above floor.
    # post-desync anchors move WITH the desynced view -> channel cannot point at j by construction (floors only).
    assert s_gate[1] > s_null[1] + 0.05, f"instrument dead on fixture: gate ls {s_gate[1]:.3f} vs null {s_null[1]:.3f}"
    print("fixture OK (instrument responds to cross-channel disagreement)")


if __name__ == "__main__":
    identity_rotation_check()   # frame-free fixture first: validates the score family responds at all
    negp = []; negl = []; posp = []; posl = []; dnp = []; dnl = []; dpp = []; dpl = []
    for seed in range(120):
        k, x, a, j, _, _ = trial_anchored(2 * seed);                       pw, ls = anchor_score(k, x, a); negp.append(pw); negl.append(ls)
        k, x, a, j, _, _ = trial_anchored(2 * seed + 1);                   pw, ls = anchor_score(k, x, a); posp.append(pw); posl.append(ls)
        k, x, a, j, _, _ = trial_anchored(2 * seed, anchor_post=True);     pw, ls = anchor_score(k, x, a); dnp.append(pw); dnl.append(ls)
        k, x, a, j, _, _ = trial_anchored(2 * seed + 1, anchor_post=True); pw, ls = anchor_score(k, x, a); dpp.append(pw); dpl.append(ls)
    negp, negl, posp, posl = map(np.array, (negp, negl, posp, posl))
    print(f"E3b ONE-SHOT gate arm: pairwise AUROC = {auroc(posp, negp):.3f} | LS AUROC = {auroc(posl, negl):.3f}   (gate: survive iff >= 0.85)")
    print(f"post-desync anchors DIAGNOSTIC: pairwise {auroc(np.array(dpp), np.array(dnp)):.3f} / LS {auroc(np.array(dpl), np.array(dnl)):.3f} (expected ~chance: same channel cannot see desync)")
    oneg = np.array([oracle_ls(2 * seed) for seed in range(120)])
    opos = np.array([oracle_ls(2 * seed + 1) for seed in range(120)])
    print(f"ORACLE-LS ceiling (post-hoc diagnostic, TRUE angles): null mean {oneg.mean():.3f} | pos mean {opos.mean():.3f} -> AUROC = {auroc(opos, oneg):.3f}")
