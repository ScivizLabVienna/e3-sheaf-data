"""E10 baseline-proxy (pre-registered findings.md 2026-11-10 BEFORE run; one shot, no tuning after verdict).
Statistic (frozen): pairwise photometric stitching-QA score = mean over the 4 quadrant windows of masked mean |A - shift(B, -m)|; structure mask per window = |grad| above its median; m = measured phase-correlation offset of that pair on the same crop (EMSIQA/OFSIQA recipe, re-implemented proxy; disclosed as proxy).
Null: all K x NP clean pair-scores. Trial mirrors e6b in image domain: pick one frame node v (1..K-1) inside window start i; rendering frame i+v with the wrong chain transform (defect d = random_sign x SIGC x level on edge (v-1,v)) misaligns exactly pairs (v-1,v) and (v,v+1); those 2 scores are positives, all clean scores negatives.
GATE G-E10 (frozen): proxy max-AUROC >= 0.9 at level <= 3 x sigma_c -> pairwise baseline beats the sheaf channel, paper re-framed with a comparative loss row; else tie/loss for baseline -> Table-1 column. N_shift class omitted by design: same-view pairwise scores gauge it away (view-gauge theorem, different mask)."""
import numpy as np, tifffile as tf, os
from scipy.ndimage import shift as ndshift
from scipy.stats import rankdata

HERE = os.path.join(os.path.dirname(__file__), "..")
PATH = os.environ.get("E6B_ROI") or os.path.join(HERE, "data", "ROI_1584-6996-1.tiff")
SIGC = np.load(os.environ.get("E6B_SIGMA_NPZ") or os.path.join(HERE, "e6b_sigma.npz"))["sig"]
K, NP, TRIALS, SEED, GLAG = 6, 60, 40, 11, 30
LEVELS = (0.5, 1.0, 2.0, 3.0, 5.0)
CROP, W2 = 512, 256
QUADS = [(0, 0), (0, W2), (W2, 0), (W2, W2)]


def auroc_ci(pos, neg, n=2000):
    def au(p, q):
        r = rankdata(np.concatenate([p, q]))
        return (r[: len(p)].sum() - len(p) * (len(p) + 1) / 2) / (len(p) * len(q))
    rng = np.random.default_rng(7)
    bs = [au(rng.choice(pos, len(pos)), rng.choice(neg, len(neg))) for _ in range(n)]
    return au(pos, neg), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def phase512(fa, fb):  # frozen law = e6_measure.phase_shift on CROP windows
    w = np.outer(np.hanning(CROP), np.hanning(CROP))
    cc = np.fft.irfft2(np.fft.rfft2(fa * w) * np.conj(np.fft.rfft2(fb * w)), s=fa.shape)
    pk = np.unravel_index(np.argmax(cc), cc.shape)

    def parab(idx, axis):
        n = cc.shape[axis]
        f0 = cc[pk[:axis] + ((idx - 1) % n,) + pk[axis + 1:]]; f1 = cc[pk]; f2 = cc[pk[:axis] + ((idx + 1) % n,) + pk[axis + 1:]]
        d = (f0 - f2) / (2 * (f0 - 2 * f1 + f2)) if (f0 - 2 * f1 + f2) != 0 else 0.0
        return float(pk[axis] + np.clip(d, -0.5, 0.5))
    dy, dx = parab(pk[0], 0), parab(pk[1], 1)
    if dy > CROP // 2: dy -= CROP
    if dx > CROP // 2: dx -= CROP
    return np.array([dx, dy])


vol = tf.memmap(PATH, mode="r")
NF = vol.shape[0]
c0 = (vol.shape[2] - CROP) // 2
CACHE, MASKS = {}, {}


def get(f):
    if f not in CACHE:
        CACHE[f] = np.asarray(vol[f, c0:c0 + CROP, c0:c0 + CROP], dtype=np.float64)
    return CACHE[f]


def masks_for(f):
    if f not in MASKS:
        A, M = get(f), []
        for (y, x) in QUADS:
            a = A[y:y + W2, x:x + W2]
            g = np.abs(np.diff(a, axis=0, prepend=a[:1])) + np.abs(np.diff(a, axis=1, prepend=a[:, :1]))
            M.append(g > np.median(g))
        MASKS[f] = M
    return MASKS[f]


rng = np.random.default_rng(SEED)
starts = np.sort(rng.choice(NF - K - GLAG + 1, NP, replace=False))
OFFS = {}
for i in starts:
    for f in range(i, i + K + 1): get(f)
    OFFS[i] = np.array([phase512(get(i + e), get(i + e + 1)) for e in range(K)])
CACHE.clear()  # frames re-read from memmap on demand; offsets/masks persist


def pair_score(i, e, d=(0.0, 0.0)):
    A, B = get(i + e), get(i + e + 1)
    m = OFFS[i][e] + np.asarray(d, dtype=float)
    tot = 0.0
    for q, (y, x) in enumerate(QUADS):
        slc = (slice(y, y + W2), slice(x, x + W2))
        a = A[slc]
        bs = ndshift(B[slc], (-m[1], -m[0]), order=1, mode="nearest")
        tot += float(np.abs(a - bs)[masks_for(i + e)[q]].mean())
    return tot / 4.0


null = np.array([pair_score(i, e) for i in starts for e in range(K)])
out = [f"N pairs (window starts x K) = {len(null)}; fixture null mean {null.mean():.2f}"]
for lvl in LEVELS:
    pos = []
    for t in range(TRIALS):
        i = int(starts[t % len(starts)])
        v = 1 + int(rng.integers(K - 1))          # frame node carrying the wrong chain offset
        d = rng.choice([-1.0, 1.0], size=2) * SIGC * lvl
        for ee in (v - 1, v):                     # both pairs rendered against the mis-stitched frame
            dd = d if ee == v - 1 else -d         # pair (v-1,v): B carries +d ; pair (v,v+1): relative error -d
            pos.append(pair_score(i, ee, dd))
    a, lo, hi = auroc_ci(np.array(pos), null)
    out.append(f"E10 baseline-proxy level {lvl:.1f}: AUROC {a:.3f} CI[{lo:.3f},{hi:.3f}]")
best3 = max(float(r.split("AUROC ")[1].split(" ")[0]) for r in out[1:] if float(r.split("level ")[1].split(":")[0]) <= 3.0)
out.append("VERDICT: " + ("BASELINE BEATS (>=0.9 at <=3x sigma_c) -> paper re-framed with comparative loss" if best3 >= 0.9 else "tie/loss for baseline at matched relative scale -> Table-1 comparative column"))
txt = "\n".join(out)
print(txt)
open(os.path.join(HERE, "e10_results.txt"), "w").write(txt + "\n")
