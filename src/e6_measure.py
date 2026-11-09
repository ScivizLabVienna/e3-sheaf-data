"""E6 round-13 leg: REAL pairwise translation noise on EMPIAR-10478 ROI (pre-registration findings.md round 12).
Emits per-pair measured offsets + robust sigma_t BEFORE any injection. Frozen here; injection trials reuse this file's numbers."""
import numpy as np, tifffile as tf, sys, os

PATH = os.path.join(os.path.dirname(__file__), "..", "data", "ROI_1584-6996-1.tiff")
CROP, LAGS, NFIRST = 512, (10, 30), 100


def crop(img):
    c = img.shape[1] // 2 if img.ndim == 3 else img.shape[0] // 2
    a = img[..., c - CROP // 2:c + CROP // 2, c - CROP // 2:c + CROP // 2] if img.ndim == 3 else img[c - CROP // 2:c + CROP // 2, c - CROP // 2:c + CROP // 2]
    return a.astype(np.float64)


def phase_shift(fa, fb):                                              # shift s.t. shifting b by -s matches a; parabolic subpixel (frozen method)
    w = np.outer(np.hanning(CROP), np.hanning(CROP))
    F = np.fft.rfft2(fa * w); G = np.fft.rfft2(fb * w)
    cc = np.fft.irfft2(F * np.conj(G), s=fa.shape)
    pk = np.unravel_index(np.argmax(cc), cc.shape)
    def parab(idx, axis):                                             # 1D parabola through peak +-1 (periodic)
        n = cc.shape[axis]
        f0 = cc[tuple(pk[:axis] + ((idx - 1) % n,) + pk[axis + 1:])]
        f1 = cc[pk]; f2 = cc[tuple(pk[:axis] + ((idx + 1) % n,) + pk[axis + 1:])]
        d = (f0 - f2) / (2 * (f0 - 2 * f1 + f2)) if (f0 - 2 * f1 + f2) != 0 else 0.0
        return float(pk[axis] + np.clip(d, -0.5, 0.5))
    dy = parab(pk[0], 0); dx = parab(pk[1], 1)
    n0, n1 = cc.shape
    if dy > n0 / 2: dy -= n0
    if dx > n1 / 2: dx -= n1
    return float(dx), float(dy)


if __name__ == "__main__":
    vol = tf.memmap(PATH, mode="r")
    print("shape", vol.shape, "dtype", vol.dtype)
    out = []
    for lag in LAGS:
        ds = []
        for i in range(NFIRST):
            a = crop(np.asarray(vol[i])); b = crop(np.asarray(vol[i + lag]))
            ds.append(phase_shift(a, b))
        D = np.array(ds)
        med = np.median(D, axis=0); resid = D - med
        sig = 1.4826 * np.median(np.abs(resid - np.median(resid, axis=0)), axis=0)   # robust per-component sigma (MAD)
        print(f"lag {lag}: median offset ({med[0]:.3f},{med[1]:.3f}) px | robust sigma_t = ({sig[0]:.4f},{sig[1]:.4f}) px")
        out.append((lag, D))
    D30 = out[1][1]
    np.savez(os.path.join(os.path.dirname(__file__), "..", "e6_pairs_lag30.npz"), D=D30,
             med=np.median(D30, axis=0), sigma=1.4826 * np.median(np.abs(D30 - np.median(D30, axis=0)), axis=0))
    print("saved e6_pairs_lag30.npz (frozen pair offsets + sigma)")
