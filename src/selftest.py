"""Assert-based sanity checks for sheafcore (self-check rule). Run: python src/selftest.py"""
import numpy as np, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from sheafcore import build_deltas, betti, harmonic_energy

V = list(range(5)); E = [(0,1),(1,2),(2,3),(3,4),(0,4)]; F = []          # 5-cycle pose graph
d0, d1 = build_deltas(V, E, F)
assert tuple(int(v) for v in betti(d0, d1)) == (1, 1, 0), betti(d0, d1)  # known H^0/H^1 of C5
x = np.array([3.,-2.,0.5,1.,7.])                                          # one desynced edge (cycle holonomy 9.5 != 0)
assert harmonic_energy(x, d0, d1) > 0                                     # H^1 carrier hit -> nonzero
y = np.random.default_rng(0).normal(size=len(V))
assert harmonic_energy(d0 @ y, d0, d1) < 1e-9                             # exact cochain delta_0 y (global pose field) -> zero harmonic part
e7 = E + [(2,4)]                                                          # chord -> 2 indep cycles; fill triangle 2-3-4 kills ONE
d0b, d1b = build_deltas(V, e7, [(2,3,4)])
assert tuple(int(v) for v in betti(d0b, d1b))[:2] == (1, 1)               # outer C5 cycle survives as the only H^1 generator
z = np.array([9.]); x7 = d1b.T @ z                                        # defect = literally a face boundary row: pure curvature, zero cohomology
assert harmonic_energy(x7, d0b, d1b) < 1e-9                               # curvature correction absorbs it exactly...
assert harmonic_energy(np.delete(x7, 5), d0, d1) > 0                      # ...but on the face-free pose graph (drop chord edge idx5) the SAME defect registers as H^1 holonomy (E3 mode: faces stay OUT so holonomy visible)
print("selftest OK")
