"""E12 synthetic-warp ground truth (pre-reg findings.md E12 BEFORE run; one-shot; branches P1/P2 frozen there).
Real ROI1 faces rigidly translated by KNOWN t_f ~ iid N(0,1.5^2) px (seed 31337); crop/phase frozen from e6b_measure; detector+trial protocol frozen from e6b_trials (K=6, LAG=30, NW=60, LEVELS, seeds 5000+wi[+90000]). Truth known -> closure residuals = pure measurement-physics error, no stitcher in loop.
shortcut: rigid per-face translation only; nonrigid warp out of scope (pre-registered)."""
import numpy as np, tifffile as tf, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from e6b_measure import crop, phase_shift, K, GLAG
NW = 151 - (K + GLAG) + 1                               # same window count as frozen real measurements (full usable face range of ROI1, NF=151)
LAG = GLAG
import e6b_trials as E

HERE = os.path.join(os.path.dirname(__file__), "..")
LEVELS = (0.5, 1.0, 2.0, 3.0, 5.0)
TRUTH = {i: v for i, v in enumerate(np.random.default_rng(31337).normal(0, 1.5, (NW + K + LAG + 1, 2)))}
_cache = {}


def render(i):
    if i not in _cache:
        from scipy.ndimage import shift
        a = np.pad(crop(np.asarray(VOL[i])), ((64, 64), (64, 64)))
        t = TRUTH[i]
        _cache[i] = shift(a, (-t[1], -t[0]), order=3, mode="grid-wrap")[64:-64, 64:-64] if np.abs(t).max() > 1e-9 else a[64:-64, 64:-64].copy()
    return _cache[i]


VOL = tf.memmap(os.path.join(HERE, "data", "ROI_1584-6996-1.tiff"), mode="r")
ADJ = np.zeros((NW, K, 2)); GLO = np.zeros((NW, K + 1, 2))
for i in range(NW):
    gf = i + LAG
    for e in range(K):
        ADJ[i, e] = phase_shift(render(i + e), render(i + e + 1))
    for m in range(K + 1):
        GLO[i, m] = (0.0, 0.0) if i + m == gf else phase_shift(render(gf), render(i + m))

err = np.array([[ADJ[i, e] - (TRUTH[i + e + 1] - TRUTH[i + e]) for e in range(K)] for i in range(NW)])
print("measured-vs-truth |err| median %.3f p95 %.3f px (renderer+phase error only)" % (np.median(np.abs(err)), np.percentile(np.abs(err), 95)))

E.ADJ, E.GLO = ADJ, GLO
R = []
for w in range(30, NW):
    A, b = E.rows_for(w)
    x = np.linalg.lstsq(A, b, rcond=None)[0]
    R.extend(A @ x - b)
R = np.array(R).reshape(-1, 2)                          # rows_for rhs is (rows,2): one column per pixel axis
SIGC = np.array([1.4826 * np.median(np.abs(R[:, c] - np.median(R[:, c]))) for c in (0, 1)])
E.SIGC = SIGC
informative = 0.3 <= float(SIGC.mean()) <= 3.0
lines = ["sigma_c synth = (%.3f,%.3f) px | P1 branch: %s" % (SIGC[0], SIGC[1], "INFORMATIVE" if informative else "UNINFORMATIVE (pre-reg disclosure branch)")]

from run_p1 import auroc
wins = list(range(30, NW))
null = [E.score(w, ADJ[w], GLO[w]) for w in wins]
firstgate = None; nsh_max = 0.0
for kind in ("M_edge", "N_shift"):
    for lvl in LEVELS:
        s = []
        for wi, w in enumerate(wins):
            rng = np.random.default_rng(5000 + wi + (0 if kind == "M_edge" else 90000))
            adjp, glp = E.trial(w, rng, kind, lvl)
            s.append(E.score(w, adjp, glp))
        a = auroc(s, null); lo, hi = E.boot(np.array(s), np.array(null))
        lines.append("%s level %.1f: AUROC %.3f CI[%.3f,%.3f]" % (kind, lvl, a, lo, hi))
        if kind == "M_edge":
            if firstgate is None and a >= 0.9 and lo > 0.5: firstgate = lvl
        else:
            nsh_max = max(nsh_max, a)
branch = "uninformative(P1)" if not informative else ("<=2x STITCHER-CONFOUND" if firstgate in (0.5, 1.0, 2.0) else ("CONFIRMED {3,5}x" if firstgate in (3.0, 5.0) else ">5x/NONE renderer-bug branch"))
lines.append("P2: first M_edge gate level = %s -> %s" % (firstgate, branch))
lines.append("N_shift gauge check (theory ~0.5): max AUROC %.3f" % nsh_max)
txt = "\n".join(lines)
print(txt)
open(os.path.join(HERE, "e12_synth_results.txt"), "w").write(txt + "\n")
np.savez(os.path.join(HERE, "e12_sigma.npz"), sig=SIGC)
np.savez(os.path.join(HERE, "e12_meas.npz"), ADJ=ADJ, GLO=GLO, truth=np.array([TRUTH[i] for i in range(len(TRUTH))]))
