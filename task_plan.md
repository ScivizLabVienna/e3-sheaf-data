# E3 — Sheaf-on-data: computable inconsistency for scientific visualization data

Premise (from verified-real cluster arXiv 2605.16785 / 2601.15320 / 2511.11092): a scaffolded cell complex over measurement space, with data as sections of a cellular sheaf, makes INCONSISTENCY computable: H^0 = globally consistent components, H^1 = unavoidable contradictions (obstructions). For SciVizLab this is the lab-identity experiment — quantify inconsistency across multiple reconstructions/views of the same specimen (exactly what multi-view 3D capture + tomography produce).

## Phases
- [ ] P0 — data discovery: inspect C:/Users/ZID/sciviz-pipeline/data/out for local scan assets (point clouds/meshes from earlier COLMAP/Gaussian-splat runs; 2026-11-06 ls confirms 7 timestamped job dirs exist there, oldest probe material fixture_img.png/wav also present); fallback = synthetic k=views registration toy. Decide substrate, log here.
- [x] P0-lib — tooling reality check 2026-11-06: `sheafapy` and `gudhi-hera` are NOT on PyPI (uv dry-run both "not found"). Options found via search: pysheaf (kb1dds, reference impl from Hansen/V.Ghrist line, git-install only, py3.6-era -> breakage risk on 3.11), uriyaf/sheaves (research code, cohomology), or **home-rolled numpy/scipy sparse coboundary solver for scaffolded complexes <=50 cells (~60 lines)** — chosen default (lazy + fully controlled); gudhi already installed for complexes anyway.
- [ ] P1 — implement toy: n-view registration graph -> scaffold = views+overlaps complex, data = per-view intensity/transform estimates; compute H^0/H^1 with sparse linalg; metric: injected-desync detection AUROC vs consistency-radius threshold baseline (the obvious non-sheaf competitor).
- [ ] P2 — real substrate only if P1 AUROC > baseline by pre-registered margin.

## Gate
- P1 kill criterion pre-registered: sheaf H^1 desync detection must beat consistency-radius baseline AUROC by >= 0.05 else project archived as NULL with writeup (negative results count).
