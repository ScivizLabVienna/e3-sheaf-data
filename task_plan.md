# E3 — Sheaf-on-data: computable inconsistency for scientific visualization data

Premise (from verified-real cluster arXiv 2605.16785 / 2601.15320 / 2511.11092): a scaffolded cell complex over measurement space, with data as sections of a cellular sheaf, makes INCONSISTENCY computable: H^0 = globally consistent components, H^1 = unavoidable contradictions (obstructions). For SciVizLab this is the lab-identity experiment — quantify inconsistency across multiple reconstructions/views of the same specimen (exactly what multi-view 3D capture + tomography produce).

## Phases
- [x] P0 — data discovery DONE 2026-11-06: sciviz-pipeline/data/out holds 9 dirs of TouchDesigner job outputs (td_spec.json + preview PNGs; one 143M dir = splat-intent job with only raw mp4 inputs, zero .ply/.splat/mesh/colmap assets anywhere — see findings.md round 1). **Decision: synthetic k-views registration toy** (fallback route); real-substrate path via 19e0dd videos kept open but not needed for P1 gate.
- [x] P0-lib — tooling reality check 2026-11-06: `sheafapy` and `gudhi-hera` are NOT on PyPI (uv dry-run both "not found"). Options found via search: pysheaf (kb1dds, reference impl from Hansen/V.Ghrist line, git-install only, py3.6-era -> breakage risk on 3.11), uriyaf/sheaves (research code, cohomology), or **home-rolled numpy/scipy sparse coboundary solver for scaffolded complexes <=50 cells (~60 lines)** — chosen default (lazy + fully controlled); gudhi already installed for complexes anyway.
- [x] P1 — **NULL 2026-11-06 (round 4).** Frozen run: sheaf AUROC .545 vs baseline .513, delta +0.033 (CI [-0.061,+0.132]) < +0.05 gate → project archives NULL per pre-registration one-shot rule. Mechanism finding in findings.md: view-level translation desync is pure gauge on a face-free pose cycle — H^1 and consistency radius are both structurally blind to it; the negative result itself ships as E3's contribution. `src/run_p1.py` + `p1_results.txt` committed as frozen evidence.
- [x] P2 — not reached: precondition "P1 AUROC > baseline by pre-registered margin" failed → archived with P1 (NULL).
- [x] Round 5 (2026-11-08, operator discretion) — post-hoc two-sided characterization appended to findings.md: signed |holonomy| arm sensitive to measurement defects (.591/.659, near theory cap .63), all four cycle statistics blind to view desync (≤.508); power-starvation of the pre-reg SNR disclosed; round-4 wording corrected. `src/characterize.py` + `characterize_results.txt`. Not a re-gate. E3 phases now exhausted — project closed pending any operator-authorized future spec (anchors).


## Gate
- P1 kill criterion pre-registered: sheaf H^1 desync detection must beat consistency-radius baseline AUROC by >= 0.05 else project archived as NULL with writeup (negative results count).
