"""Home-rolled coboundary solver, R-coefficient 2-dim complexes (<=50 cells).
Stored deltas ARE coboundary maps: d0 = |E|x|V| (exact cochain of vertex field y is d0 @ y), d1 = |F|x|E|? NO - d1 built as face-boundary rows: d1[t] has +-1 on triangle t's edges, so delta_1^T rows = d1 and im(curvature) = ROW space of d1. Everything below is pinned by selftest.py + 7-case betti regression; trust those."""
import numpy as np

def build_deltas(V, E, F):
    """V vertex list, E oriented edges (a,b), F triangles (p,q,r) whose 3 edges appear in E (either orientation). Returns d0 (|E|x|V|), d1 (|F|x|E|)."""
    ni, ne = len(V), len(E)
    idx = {v: i for i, v in enumerate(V)}
    ei = {}
    d0 = np.zeros((ne, ni))
    for i, (a, b) in enumerate(E):
        ei[frozenset((a, b))] = i
        d0[i, idx[a]] = -1.0; d0[i, idx[b]] = 1.0
    d1 = np.zeros((len(F), ne))
    for t, (p, q, r) in enumerate(F):
        for e, sgn in (((p, q), 1.0), ((p, r), -1.0), ((q, r), 1.0)):  # d[pqr] = [pq]-[pr]+[qr]
            k = ei.get(frozenset(e))
            assert k is not None, f"triangle {(p,q,r)} missing edge {e}"
            if E[k][0] != e[0]:
                sgn = -sgn  # stored orientation reversed
            d1[t, k] = sgn
    return d0, d1

def _nullity(M):
    if M.size == 0:
        return M.shape[1]
    return M.shape[1] - np.linalg.matrix_rank(M)

def betti(d0, d1):
    """Cohomology Betti numbers via Hodge-Laplacian nullities (pinned by 7-case regression table)."""
    b0 = _nullity(d0.T @ d0)                    # vertex-space Laplacian: ker = locally constant fields = components
    L1 = (d0 @ d0.T) + (d1.T @ d1 if d1.size else 0)   # edge space: delta_0 delta_0^T + delta_1^T delta_1
    b1 = _nullity(L1)
    b2 = _nullity(d1 @ d1.T) if d1.size else 0  # face-space Laplacian
    return (b0, b1, b2)

def harmonic_energy(x, d0, d1):
    """||H(x)||^2 for edge-vector x: residual after projecting out COL space of [d0 | d1.T] = im(exact cochains delta_0 y = d0 @ y) + im(curvature corrections delta_1^T z = d1.T @ z). F empty (pose-graph mode) = sum of squared cycle holonomy defects — inconsistency NO global pose re-estimation can remove."""
    Dx = np.concatenate([d0] + ([d1.T] if d1.size else []), axis=1)   # columns span im(exact)+im(curvature); lstsq residual = harmonic (H^1) part exactly
    xhat = np.linalg.lstsq(Dx, x, rcond=None)[0]
    return float(np.sum((x - Dx @ xhat) ** 2))
