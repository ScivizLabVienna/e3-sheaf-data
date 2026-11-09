"""E6b (frozen pre-verdict correction, findings.md round-14 disclosure). One-shot.
Nodes 0..K (K=6); ADJACENT rows = phase-corr offsets lag-10; GLOBAL rows = wide-baseline (+30 frame) content match to window start, treated as FIXED absolute-path observations (the way stitchers use stage/bead anchors — free-floating globals made view-desync an exact gauge, proven round 14).
Score = max |global-row residual| after weighted LS on all difference rows. Injection levels in units of MEASURED triangle-closure sigma (emitted before trials)."""
import numpy as np, tifffile as tf, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from run_p1 import auroc
from e6_measure import crop, phase_shift

PATH = os.environ.get("E6B_ROI") or os.path.join(os.path.dirname(__file__), "..", "data", "ROI_1584-6996-1.tiff")  # E6B_ROI: E8 replication ROI
K, GLAG, ALAG = 6, 30, 10


def measure():
    vol = tf.memmap(PATH, mode="r"); NF = vol.shape[0]; nwin = NF - (K + GLAG) + 1  # NF from file (was hardcoded 151; second ROI frame count differs)   # windows fully inside file: start i, nodes i..i+K, globals to i+GLAG<=150 -> i <= 151-K-GLAG=139... careful: global pair (node i+m, ref i+GLAG): both frames exist iff i+GLAG<151; window needs i+K<151 too
    ADJ = np.zeros((nwin, K, 2)); GLO = np.zeros((nwin, K + 1, 2))
    cache = {}
    for i in range(nwin):
        for f in range(i, i + K + 1):
            cache[f] = crop(np.asarray(vol[f]))
        gf = i + GLAG
        if gf not in cache: cache[gf] = crop(np.asarray(vol[gf]))
        for e in range(K):
            ADJ[i, e] = phase_shift(cache[i + e], cache[i + e + 1])       # P_{i+e+1}-P_{i+e}
        for m in range(K + 1):
            GLO[i, m] = (0.0, 0.0) if i + m == gf else phase_shift(cache[gf], cache[i + m])   # P_{i+m} - P_{i+GLAG}; exact 0 when node IS the ref window (start<=29; disclosed artifact)
        for f in list(cache):                                             # rolling: keep only frames used by next window
            if f < i: cache.pop(f)
    return ADJ, GLO


if __name__ == "__main__":
    ADJ, GLO = measure()
    np.savez(os.path.join(os.path.dirname(__file__), "..", "e6b_meas.npz"), ADJ=ADJ, GLO=GLO)
    # convention check: closures c_m = (G_m - G_{m+1}) + adj_m must be small for correct sign; try both orientations, pick the one with |median| closer to 0 in BOTH components (convention fix, pre-results)
    def closures(ADJ, GLO, sgn):
        return np.stack([GLO[:, m] - GLO[:, m + 1] + sgn * ADJ[:, m] for m in range(K)], axis=1)
    best = None
    for sgn in (1.0, -1.0):
        C = closures(ADJ, GLO, sgn); med = np.abs(np.median(C.reshape(-1, 2), axis=0)).sum()
        if best is None or med < best[0]: best = (med, sgn)
    SGN = best[1]
    C = closures(ADJ, GLO, SGN)
    med = np.median(C.reshape(-1, 2), axis=0)
    R = C - med
    SIGC = 1.4826 * np.median(np.abs(R.reshape(-1, 2) - np.median(R.reshape(-1, 2), axis=0)), axis=0)   # robust closure sigma per component = frozen noise scale
    print(f"sign={SGN} closure median ({med[0]:.3f},{med[1]:.3f}) px | CLOSURE SIGMA ({SIGC[0]:.3f},{SIGC[1]:.3f}) px  [emitted BEFORE injections]")
    np.savez(os.path.join(os.path.dirname(__file__), "..", "e6b_sigma.npz"), sig=SIGC, sgn=SGN, med=med)
