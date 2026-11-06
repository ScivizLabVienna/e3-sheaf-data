# E3 findings (append-only per round)

## P1 PRE-REGISTRATION (written 2026-11-06 BEFORE first run; gate text unchanged, frozen)

Protocol for injected-desync AUROC experiment (`src/run_p1.py`, fixed before execution):
- **Substrate:** synthetic k-view registration, k ∈ {5,6,7} rotating by seed%3. Poses g_i ~ SE(2): theta~U(-pi/2,pi/2), t~N(0,I₂). Scaffold = cycle graph C_k pose graph (chain edges (i,i+1) + closure edge); F=∅ deliberately (pose-graph mode; no Cech faces forced).
- **Data:** each shared-edge measurement m_ij = log(g_i⁻¹g_j ⊕ ε), ε ~ N(0, σ²I₂ × rot 0.05 rad), σ=0.10. SE(2) group composition (nonlinear; not a plain additive toy).
- **Injection:** view-level desync — one random view's pose offset by s·σ in translation before all its edge measurements recomputed (views are ground truth; edges never directly corrupted). s ∈ {1.5, 2.5} alternating; null trials s=0.
- **Trials:** 240 total (seeds 0..239), 120 pos / 120 neg, k rotating. Both arms score the identical x-vector per trial.
- **Sheaf arm:** harmonic_energy(x, d0, d1) — Hodge harmonic part of the pose 1-form = total cycle holonomy defect (H^1 carrier magnitude; dim H^1 itself is topological and constant, so detection power lives in the harmonic representative energy).
- **Baseline arm (frozen competitor):** consistency radius = max per-edge residual norm after closed-form linear LS pose synchronization (the obvious non-sheaf method named in task_plan).
- **Metric:** AUROC via Mann-Whitney U + 2000-resample bootstrap CI.
- **Gate decision rule:** project survives only if |AUROC_sheaf − AUROC_baseline| ≥ 0.05 with the advantage required for "sheaf wins"; otherwise E3 archives NULL (negative result counts). One-shot: numbers do not move the gate.
- **Declared hazard (intellectual honesty):** for R-coefficients on a face-free complex, Hodge theory gives harmonic energy ≡ cycle-consistency defect analytically; any true separation must arise from SE(2) log-domain nonlinearity or outlier structure. Expected effect small; we run it anyway because the pre-registered claim is exactly this discriminator.

## lit-scan 2026-11-06 (round 2; 4 searches: direct / adjacent / far-lens radar + ID verify)

- arXiv:2601.19056 — "Relative Obstructions and Spectral Diagnostics for Sheaves on Cell Complexes" (verified) — spectral witnesses: project signal onto sheaf-Laplacian high-eigenvalue modes / harmonic residual energy as graded (not binary) inconsistency score with per-cell localization — **adopt as P1 spec proposal**: H^1 detector = norm of harmonic projection of the coboundary residual (energy form), threshold pre-registered from null runs.
- arXiv:2208.07103 — "Global Consistent Point Cloud Registration Based on Lie-algebraic Cohomology" (verified) — pose 1-forms on a Cech/viewing complex; loop product = identity iff the 1-form is a coboundary; their Poisson/Hodge correction = MINIMIZING inconsistency, i.e. exactly what our frozen consistency-radius baseline does; cocycle defect on loops is the same H^1 class we keep uncorrected — **adopt as spec proposal**: scaffold data = SE(2) pose 1-forms (log map to R^3 for linear sheaf), and it independently confirms the chosen baseline is the right non-sheaf competitor.
- arXiv:2102.09719 — "Signal Detection in Distributed MIMO Radar with Non-Orthogonal Waveforms and Sync Errors" (verified) — FAR LENS radar/sonar matched filtering: sync errors move matched-filter sampling off the ambiguity-function peak => detection power collapses against a mis-specified detector; GLRT detectors designed around that off-peak signature port to our injected-desync design: pick desync magnitudes *known* to push harmonic-residual energy off-baseline and pre-register the threshold from null variance, never tune on test seeds — **adopt as methodology only** (does not touch the frozen gate).

No evaluator/metric/gate edits above — all three enter as P1 spec/parameter proposals per campaign rules.

## Round 1 — P0 substrate decision (2026-11-06)

**Inventory of C:/Users/ZID/sciviz-pipeline/data/out (9 dirs, not 7):**

| dir | size | contents |
|---|---|---|
| 20260717-164026-307baa | 1K | td_spec.json only (failed/test image job) |
| 20260717-164639-895a18 / -164758-73f87c / -164927-59c5a4 | 236K ea | td_spec.json + preview.png |
| 20260717-164957-173e78 | 264K | td_spec.json + preview.png + spectrogram.png |
| 20260729-181347-e73626 | 264K | td_spec.json + preview.png + spectrogram.png |
| 20260729-181454-19e0dd | 143M | td_spec.json ("turn these videos into gaussian splats") + 2 input mp4 (VID_20251105_*) — **no splat/pointcloud/mesh output** |
| TEST-164207-1e223 / TEST-AUD-164223-cf88f | 236K/28K | TouchDesigner test job outputs |

**Verdict:** these are TouchDesigner audio-reactive visual job outputs (td_spec.json + PNG previews), not COLMAP/splat reconstruction products. Recursive find for `*colmap*|*.ply|*.splat|*.obj|*.xyz` across all dirs: zero hits. The one splat-intent job (19e0dd) holds only raw video inputs — pipeline never produced the asset. No pose/mesh/pointcloud data => cannot build a real >=2-view substrate of one specimen.

**Decision: fallback route per task_plan — synthetic k-views registration toy.** One known 2-D scene observed by k views; per-view data = rigid-transform estimate + landmark correspondences; ground-truth consistency known; inject desync in subsets of views for the AUROC experiment (P1). Real-substrate option stays open: the 2 Quest mp4s in 19e0dd could become a substrate later if a splat/COLMAP run is ever completed, but P1 gate does not need it.

**Env:** scipy 1.17.1 already present in homotest venv (uv dry "already satisfied"); numpy 2.4.6 + gudhi + ripser verified importable with S:/hermes/cache/scratch/homotest/Scripts/python.exe. P1 ready to start.

## Round 3 — solver implemented & validated GREEN (2026-11-06, commit 5e7a4e2)
`src/sheafcore.py` + `src/selftest.py`. Hodge-Laplacian nullities; betti regression table of 7 by-construction complexes all pass (C5→(1,1,0), chorded C5→(1,2,0), chord+faced→(1,1,0), filled tri→(1,0,0), disjoint tri+edge→(2,0,0), fig8→(1,2,0), disk quad→(1,0,0)); selftest OK; golden energy pinned (uniform 1.8 on C5 → 5.832).

- **Convention locked:** d0 = |E|x|V| incidence (exact cochain = d0 @ y), d1 = |F|x|E| face-boundary rows (curvature correction = d1.T @ z); harmonic_energy(x) = residual of projecting x out col-space[d0 | d1.T]. With F=[] this equals total inconsistency left after optimal global pose re-estimation — the GLRT matched-filter statistic from round-2 adoption.
- **Two root-cause bugs found & fixed (lesson):** (1) Laplacian-slot error b0 = nullity(d0.T@d0) vs d0@d0.T off-by-one depending on shape; (2) square-incidence transpose trap: im(d0) ≠ im(d0.T) at equal rank, so exact-cochain projection must use the *exact map's own* column space — caught only by the assert that a known exact cochain has zero energy. Prose conventions drift; asserts pin semantics.
- gudhi wheel lacks `PersistentCohomology` (AttributeError); no external oracle available → by-construction regression table + golden values are the authority.
- Pose-graph mode note: for P1 substrate F=[] deliberately, so curvature space is empty and H^1 energy = cycle holonomy defects (selftest pins both the faced-absorption and unfaced-visible behavior).

Next round: `run_p1.py` — 240-trial injected-desync AUROC per frozen pre-registration (lines 3-15 above).
