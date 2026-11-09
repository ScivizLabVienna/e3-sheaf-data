"""E6b trials on real EMPIAR-10478 measurements (frozen after round-14 disclosure; closure sigma emitted in e6b_sigma.npz BEFORE this run).
Model: unknowns q_j = P_{i+j} - P_ref (j=1..K, K=6; j=0 fixed constant = GLO_0 known when window start >= GLAG, else folded out); rows: adj diffs + global pseudo-obs. Detector = weighted max residual (all rows sigma = measured closure sigma).
Injections: M_edge = one edge row perturbed (both adj & global variants pooled) | N_shift = ALL rows of one node shifted together = rigid view desync -> GAUGE by P1 theorem -> predicted blind, descriptive only.
GATE G-E6 (frozen): any-channel AUROC >= 0.9 at level <= 3 x closure-sigma with bootstrap CI excluding 0.5 for M_edge, else synthesis FALSIFIED on real data."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from run_p1 import auroc

HERE = os.path.join(os.path.dirname(__file__), "..")
D = np.load(os.environ.get("E6B_MEAS_NPZ") or os.path.join(HERE, "e6b_meas.npz")); ADJ, GLO = D["ADJ"], D["GLO"]  # env override for E8 ROI2
S = np.load(os.environ.get("E6B_SIGMA_NPZ") or os.path.join(HERE, "e6b_sigma.npz")); SIGC = S["sig"]; MED = S["med"]
NW, K = ADJ.shape[0], ADJ.shape[1]
LEVELS = (0.5, 1.0, 2.0, 3.0, 5.0)


def rows_for(w):                                 # returns A,b for one window; rhs uses adj & GLO_M (both raw); constant column dropped (known)
    g0 = GLO[w, 0]
    A = np.zeros((2 * K + 2 * K, 2 * K)); b = np.zeros(2 * K + 2 * K)
    for e in range(K):                           # adj: q_{e+1} - q_e - [j==0]*g0 = adj_e  (q_0 := g0 known constant moved to rhs)
        A[2 * e, 2 * e] += 1                     # col for node e+1 is 2e
        b[2 * e] += ADJ[w, e, 0]
        A[2 * e + 1, 2 * e + 1] += 1; b[2 * e + 1] += ADJ[w, e, 1]
        if e >= 1:
            A[2 * e, 2 * (e - 1)] -= 1
            A[2 * e + 1, 2 * (e - 1) + 1] -= 1
        else:
            b[2 * e] += g0[0]; b[2 * e + 1] += g0[1]
    for j in range(1, K + 1):                    # global rows: q_j = GLO_j - GLO_0 + g0; rhs keeps raw GLO_j and g0 folded on left as constant
        A[2 * K + 2 * (j - 1), 2 * (j - 1)] = 1; b[2 * K + 2 * (j - 1)] = GLO[w, j, 0] - GLO[w, 0, 0] + g0[0]
        A[2 * K + 2 * (j - 1) + 1, 2 * (j - 1) + 1] = 1; b[2 * K + 2 * (j - 1) + 1] = GLO[w, j, 1] - GLO[w, 0, 1] + g0[1]
    return A, b


def score(w, adjp, glp):                         # residuals of perturbed system: r = A x_hat - b ; per-component LS weights (1/sigc^2) -> residual already in px after plain lstsq on whitened rows; report max |resid| px
    A, b = rows_for(w); A = A.copy(); b = b.copy()
    for e in range(K):
        b[2 * e] += adjp[e, 0] - ADJ[w, e, 0]; b[2 * e + 1] += adjp[e, 1] - ADJ[w, e, 1]
    for j in range(1, K + 1):
        b[2 * K + 2 * (j - 1)] += glp[j, 0] - GLO[w, j, 0]; b[2 * K + 2 * (j - 1) + 1] += glp[j, 1] - GLO[w, j, 1]
    W = np.ones(len(b))
    for e in range(K): W[2 * e] = 1 / SIGC[0]; W[2 * e + 1] = 1 / SIGC[1]
    for j in range(1, K + 1): W[2 * K + 2 * (j - 1)] = 1 / SIGC[0]; W[2 * K + 2 * (j - 1) + 1] = 1 / SIGC[1]
    sw = np.sqrt(W)[:, None]
    x = np.linalg.lstsq(sw * A, np.sqrt(W) * b, rcond=None)[0]
    res = (A @ x - b) / np.sqrt(W)               # whitened residual: dimensionless = px/sigma
    return float(np.abs(res).max())


def trial(w, rng, kind, level):
    adjp, glp = ADJ[w].copy(), GLO[w].copy()
    mag = level * float(SIGC.mean())
    if kind == "M_edge":
        e = int(rng.integers(K)); d = mag * (rng.normal(size=2) / np.linalg.norm(rng.normal(size=2)))
        adjp[e] += d
        e2 = int(rng.integers(1, K + 1))         # half the injections go to a GLOBAL row instead (alternate parity: rng bit)
        if rng.random() < 0.5:
            glp[e2] += mag * (rng.normal(size=2) / np.linalg.norm(rng.normal(size=2)))
    elif kind == "N_shift":
        j = int(rng.integers(1, K))              # interior node; ALL incident rows shifted consistently -> gauge
        d = mag * (rng.normal(size=2) / np.linalg.norm(rng.normal(size=2)))
        adjp[(j - 1) % K] += d; adjp[j] -= d    # chain passes through: edges (j-1),(j): incoming +d outgoing -d... careful convention: adj_e = q_{e+1}-q_e; shifting q_j by d => adj_{j-1}+=d, adj_j-=d
        glp[j] += d                              # direct global-to-ref match ALSO carries the desync (content moved before matching) -> exactly consistent shift of one node's rows
    return adjp, glp


def boot(x, y, n=4000, seed=7):
    rng = np.random.default_rng(seed); m = len(x) + len(y)
    xs = np.concatenate([x, y]); lab = np.zeros(m, bool); lab[:len(x)] = True
    v = []
    for _ in range(n):
        i = rng.integers(0, m, m)
        if 2 <= lab[i].sum() < m - 1: v.append(auroc(xs[i][lab[i]], xs[i][~lab[i]]))
    return float(np.quantile(v, .025)), float(np.quantile(v, .975))


if __name__ == "__main__":
    wins = list(range(30, NW))                   # skip starts<30 (global-ref lands inside node span; disclosed artifact region)
    print(f"windows used: {len(wins)} | closure sigma per px comp = ({SIGC[0]:.3f},{SIGC[1]:.3f})")
    null = [score(w, ADJ[w], GLO[w]) for w in wins]
    fixtures = []
    for lvl in (3.0,):
        adjp = ADJ[wins[0]].copy(); adjp[2] += 3 * float(SIGC.mean()) * np.array([1.0, 0])
        fixtures.append(score(wins[0], adjp, GLO[wins[0]]))
    print(f"fixture (known 3-sigc edge inj): null {null[0]:.3f} vs inj {fixtures[0]:.3f}")
    curves = {}
    for kind in ("M_edge", "N_shift"):
        curve = []
        for lvl in LEVELS:
            s = []
            for wi, w in enumerate(wins):
                rng = np.random.default_rng(5000 + wi + (0 if kind == "M_edge" else 90000))
                adjp, glp = trial(w, rng, kind, lvl)
                s.append(score(w, adjp, glp))
            a = auroc(s, null); lo, hi = boot(np.array(s), np.array(null))
            curve.append((lvl, a, lo, hi))
            print(f"{kind} level {lvl:3}: AUROC {a:.3f} CI[{lo:.3f},{hi:.3f}]")
        curves[kind] = curve
    fire = [l for l, a, lo, hi in curves["M_edge"] if a >= 0.9 and lo > 0.5]
    print("G-E6 M_edge first level meeting gate:", min(fire) if fire else "NONE -> synthesis FALSIFIED on real data")
    print("N_shift (theory-predicted gauge, descriptive): max AUROC %.3f" % max(a for _, a, _, _ in curves["N_shift"]))
