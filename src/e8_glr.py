"""E7 one-shot (pre-reg findings.md round 16): GLR energy detector on frozen e6b data/seeds."""
import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from run_p1 import auroc
import e6b_trials as E

def score_energy(w, adjp, glp):
    A, b = E.rows_for(w); A = A.copy(); b = b.copy()
    K = E.K
    for e in range(K):
        b[2*e] += adjp[e,0]-E.ADJ[w,e,0]; b[2*e+1] += adjp[e,1]-E.ADJ[w,e,1]
    for j in range(1, K+1):
        b[2*K+2*(j-1)] += glp[j,0]-E.GLO[w,j,0]; b[2*K+2*(j-1)+1] += glp[j,1]-E.GLO[w,j,1]
    W = np.ones(len(b))
    for e in range(K): W[2*e]=1/E.SIGC[0]; W[2*e+1]=1/E.SIGC[1]
    for j in range(1, K+1): W[2*K+2*(j-1)]=1/E.SIGC[0]; W[2*K+2*(j-1)+1]=1/E.SIGC[1]
    x = np.linalg.lstsq(np.sqrt(W)[:,None]*A, np.sqrt(W)*b, rcond=None)[0]
    res = (A@x-b)/np.sqrt(W)
    return float((res**2).sum())   # chi2 energy

if __name__ == "__main__":
    wins = list(range(30, E.NW))
    null = [score_energy(w, E.ADJ[w], E.GLO[w]) for w in wins]
    a1 = E.ADJ[E.wins0 if False else wins[0]].copy(); a1[2] += 3*float(E.SIGC.mean())*np.array([1.,0])
    print("fixture null %.2f inj %.2f" % (null[0], score_energy(wins[0], a1, E.GLO[wins[0]])))
    gate = None
    for lvl in E.LEVELS:
        s=[]
        for wi,w in enumerate(wins):
            rng=np.random.default_rng(5000+wi)   # identical M_edge seeds as e6b
            adjp,glp=E.trial(w,rng,"M_edge",lvl); s.append(score_energy(w,adjp,glp))
        a=auroc(s,null); lo,hi=E.boot(np.array(s),np.array(null))
        print("GLR level %.1f: AUROC %.3f CI[%.3f,%.3f]"%(lvl,a,lo,hi))
        if gate is None and a>=0.9 and lo>0.5: gate=lvl
    print("VERDICT:", ("%s -> detector suboptimality (industry 2-3xRMS heuristic rescued)"%gate) if gate and gate<=3.0 else "no level <=3 -> CHANNEL PHYSICS verdict")
