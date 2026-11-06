# E3 findings (append-only per round)

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
