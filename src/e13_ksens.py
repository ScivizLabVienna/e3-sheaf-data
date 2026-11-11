"""E13 K-sensitivity (pre-reg findings.md E13 + addendum: K=7 requires fresh measurement sets, same frozen methods/seeds/sigma-estimator; one-shot supplement)."""
import numpy as np, tifffile as tf, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from e6_measure import crop, phase_shift
import e6b_trials as E
from run_p1 import auroc
HERE = os.path.join(os.path.dirname(__file__), "..")


def measure(Kt):                                          # mirror of e6b_measure.measure with variable K (GLAG=30 frozen)
    vol = tf.memmap(os.path.join(HERE, "data", "ROI_1584-6996-1.tiff"), mode="r")
    NF = vol.shape[0]; nwin = NF - (Kt + 30) + 1
    ADJ = np.zeros((nwin, Kt, 2)); GLO = np.zeros((nwin, Kt + 1, 2)); cache = {}
    def cx(f):
        if f not in cache: cache[f] = crop(np.asarray(vol[f]))
        return cache[f]
    for i in range(nwin):
        gf = i + 30
        for e in range(Kt): ADJ[i, e] = phase_shift(cx(i + e), cx(i + e + 1))
        for m in range(Kt + 1): GLO[i, m] = (0.0, 0.0) if i + m == gf else phase_shift(cx(gf), cx(i + m))
    return ADJ, GLO


out = []
for Kt in (5, 7):
    ADJ, GLO = measure(Kt)
    E.K = Kt; E.ADJ, E.GLO = ADJ, GLO; E.NW = ADJ.shape[0]
    R = []                                                # e6b-style closure-sigma: MAD of LS residuals (estimator frozen from sigma scripts)
    for w in range(30, E.NW):
        A, b = E.rows_for(w); x = np.linalg.lstsq(A, b, rcond=None)[0]
        R.extend(A @ x - b)
    R = np.array(R).reshape(-1, 2)
    E.SIGC = SIG = np.array([1.4826 * np.median(np.abs(R[:, c] - np.median(R[:, c]))) for c in (0, 1)])
    wins = list(range(30, E.NW))
    null = [E.score(w, ADJ[w], GLO[w]) for w in wins]
    row = "K=%d sigma_c=(%.2f,%.2f):" % (Kt, SIG[0], SIG[1])
    firstgate = None; curve = []
    for lvl in (0.5, 1.0, 2.0, 3.0, 5.0):                 # full frozen LEVELS for monotonicity check
        s = []
        for wi, w in enumerate(wins):
            rng = np.random.default_rng(5000 + wi)
            adjp, glp = E.trial(w, rng, "M_edge", lvl)
            s.append(E.score(w, adjp, glp))
        a = auroc(s, null); curve.append(a)
        if firstgate is None and a >= 0.9: firstgate = lvl
        row += " %.1fx:%.3f" % (lvl, a)
    out.append(row + " | first>=0.9: %s" % firstgate)
    E.K = 6
txt = "E13 K-sensitivity on REAL ROI1 faces (fresh measure per K; same LAG/methods/seeds; sigma re-measured per K as in e6b -> levels are comparable within channel, absolute sigma differs)\n" + "\n".join(out)
print(txt)
open(os.path.join(HERE, "e13_ksens_results.txt"), "w").write(txt + "\n")
