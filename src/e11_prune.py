"""E11 RMS-prune sweep (pre-reg findings.md 2026-11-10 BEFORE run; descriptive, one-shot).
Frozen statistic = E7 GLR chi2 energy (imported from e7_glr) on frozen instruments/seeds; prune rule flag if score >= tau*rms(fixture null), tau in {1.5,2,2.5,3,3.5,4}.
Claims under test: C1 recall<0.5 at tau in {2,3} for all channels at levels<=3x; C2 inter-channel FPR spread >5x between tau=2 and 4 -> no universal tau."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import e6b_trials as E
from e7_glr import score_energy

TAUS = (1.5, 2.0, 2.5, 3.0, 3.5, 4.0)
wins = list(range(30, E.NW))
null = np.array([score_energy(w, E.ADJ[w], E.GLO[w]) for w in wins])
rms = float(np.sqrt((null ** 2).mean()))          # practitioner's RMS estimate from the same calibration pool (disclosed)
out = [f"N null windows = {len(wins)}; chi2-energy null rms = {rms:.1f}"]
rec = {}
for lvl in E.LEVELS:
    s = []
    for wi, w in enumerate(wins):
        rng = np.random.default_rng(5000 + wi)    # identical frozen seeds (e6b/e7 protocol)
        adjp, glp = E.trial(w, rng, "M_edge", lvl)
        s.append(score_energy(w, adjp, glp))
    rec[lvl] = np.array(s)
tab = []
for tau in TAUS:
    thr = tau * rms
    fpr = float((null >= thr).mean())
    rs = {lvl: float((rec[lvl] >= thr).mean()) for lvl in E.LEVELS}
    tab.append((tau, fpr, rs))
    out.append("tau %.1f (thr %.1f): FPR %.3f | recall " % (tau, thr, fpr) + " ".join("%.0fx:%.2f" % (l, rs[l]) for l in E.LEVELS))
c1 = all(rs[l] < 0.5 for tau, fpr, rs in tab if tau in (2.0, 3.0) for l in E.LEVELS if l <= 3.0)
out.append("C1 (recall<0.5 @tau{2,3}, levels<=3x): " + ("HOLDS" if c1 else "VIOLATED"))
r2, r4 = [float((null >= t * rms).mean()) for t in (2.0, 4.0)]
out.append("within-channel FPR drop ratio tau2/tau4 = %.1fx%s" % (r2 / max(r4, 1e-9), "; C2 needs cross-channel run summary (this process = one channel; compare e11 outputs of all three)"))
for tau in TAUS:                                              # guideline: smallest tau with FPR<=0.01 on THIS channel
    if float((null >= tau * rms).mean()) <= 0.01:
        out.append("tau* (FPR<=0.01) = %.1f" % tau); break
else:
    out.append("tau* (FPR<=0.01): none within sweep")
txt = "\n".join(out)
print(txt)
open(os.path.join(HERE := os.path.join(os.path.dirname(__file__), ".."), "e11_results%s.txt" % os.environ.get("E11_TAG", "")), "w").write(txt + "\n")
