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

## P1 RESULT — NULL, gate failed as pre-registered (2026-11-06 round 4)

Frozen run (`src/run_p1.py`, deterministic seeds 0..239, output archived at `p1_results.txt`):
```
n=240 pos+neg; k rotates 5/6/7
AUROC all : sheaf=0.545 baseline=0.513 delta(sheaf-baseline)=+0.033
AUROC s15 : sheaf=0.555 baseline=0.492 delta(sheaf-baseline)=+0.062
AUROC s25 : sheaf=0.536 baseline=0.533 delta(sheaf-baseline)=+0.003
delta CI95 = [-0.061, +0.132]  gate: survive iff delta >= +0.05 (pre-registered)
```
**Verdict: NULL.** Delta +0.033 < +0.05 and CI includes 0; the s=2.5 half shows no advantage at all. One-shot rule honored — numbers do not move the gate.

**Mechanism (diagnostics, not a rescue):** pre-registered injection is *view-level translation* desync (pose offset applied to one ground-truth view before remeasuring its edges). Such an offset enters the two incident edge measurements as +d and -d and **cancels in every cycle product** — it is pure gauge modulo the SE(2) commutator with neighbors, whose signal is ~theta·s·sigma ≈ 0.15 rad for s=2.5 vs rotation-noise closure std sqrt(k)·0.05 ≈ 0.13 rad at k=6. Both arms sit at chance because there is (near-)nothing to detect: H^1 cycle holonomy on a face-free pose graph is structurally blind to view-level translation desync, and consistency radius is equally blind. Supporting sensitivity probes: strength sweep needed s≈50 before the sheaf arm left chance (AUROC .762 at s=50 — nonlinear cross-coupling only); rotation-bearing injection also ≈ both arms at chance at s∈{1.5,2.5,8}. The instrument responds to defects that DO bear cycle holonomy (selftest + golden energy green), so this is a substrate-model finding, not solver failure.

**Transferable negative result (the actual E3 contribution):** on registration-cycle scaffolds, H^1/sheaf harmonics detect *measurement-level* closure defects but are provingly blind to view-level translation desync; detection of the latter needs absolute/anchor constraints (a gauge fixing in H^0 terms) — proposed for a future E4-style spec only, NOT a P1 rerun (one-shot rule).

Per pre-registration: **E3 archives NULL with this writeup.**

## lit-scan 2026-11-08 (round 5; step = position the negative result)
- arXiv:2511.02329 — incremental cycle bases for pose-graph optimization: online maintenance of cycle/homology bases could compute holonomy statistics per-update without full Hodge solve — park (efficiency, not needed for NULL writeup). [API-verified title "Incremental cycle bases for cycle-based pose graph optimization"]
- arXiv:2511.18064 — Cycle-Sync: robust cycle-consistent camera-pose synchronization with outlier loss on cycles; confirms cycle-statistic arms are current SOTA when defects are edge-level, and is the natural citation partner for our "robust_trim arm also at chance under gauge-freeing injection" control — adopt (writeup positioning only). [API-verified]
- Howard/Cochran/Moran, FUSION 2015, "Gauge-invariant registration in networks" (no arXiv id; conference-only, not open access) — registration as a network connection whose Fisher information is governed by curvature/holonomy: independent theoretical authority for the gauge-blindness mechanism claim — adopt (cite-by-venue).
- FAR LENS this round: control theory / Kalman innovation testing was the natural port (innovation-sequence residual tests are the classical non-cycle baseline; E3's consistency-radius arm already instantiates it); deliberately unrelated lens skipped, no one-sentence port found. Search budget spent (6/6).

## Round 5 — POST-HOC two-sided characterization (2026-11-08; descriptive, NOT a re-gate)
Frozen NULL stands untouched. Purpose: turn the argued mechanism into a measured two-sided claim (blind-to-X **and** sensitive-to-Y) so the negative result is citable. `src/characterize.py`, evidence `characterize_results.txt` (deterministic seeds 0..239, same noise model as pre-reg).

```
meas defect s=1.5: sheaf_H1_energy=0.518 consistency_radius=0.512 robust_trim_LS=0.506 |holonomy|_signed=0.591
view defect s=2.5: sheaf_H1_energy=0.519 consistency_radius=0.515 robust_trim_LS=0.506 |holonomy|_signed=0.508
```
(earlier ad-hoc run, meas s=2.5 signed arm = 0.659; linear-control single-defect theory caps AUROC ≈ 0.63 at these sigma/s)

Three claims, each measured:
1. **Blind-to-view-desync confirmed across four independent statistics**, including a TranSync/Cycle-Sync-style robust-trim arm (.506) and the phase-preserving |holonomy| statistic (.508): gauge-absorbable injections are not recoverable by *any* cycle-based detector at this SNR — robustness buys nothing when there is no non-gauge signal.
2. **Sensitive-to-measurement-defect confirmed only for the right statistic**: signed |cycle holonomy| reaches .591 (s=1.5) / .659 (s=2.5), near the theoretical optimum ≈ .63 for a single 0.6σ defect; scalar H^1 energy ||H||² stays at .518 because it **discards phase** — null holonomy has random per-trial sign, so the signal-defect cross-term (the power term at small s) averages out when energies are pooled unlabeled. *Correction to round-4 wording:* "rotation-bearing injection ≈ chance in both arms" was imprecise — measurement-level rotation defects ARE detectable via signed H^1 holonomy; phase-blind scalar energy is the limiter there, gauge is the limiter for view desync.
3. **Power-starvation disclosure (protocol honesty):** at pre-registered s·σ = 0.6σ_closure the optimal cycle detector itself caps near AUROC ≈ .63 and the frozen arms measured .52 — the gate region could not separate "sheaf better by ≥.05" from chance even in the best case; recorded post-hoc, no rerun (one-shot rule).

**E3 final deliverable:** negative result + measured two-sided characterization: on registration-cycle scaffolds, H^1 holonomy (phase-preserving) detects measurement-level closure defects near information-optimal, is structurally blind to view-level translation desync for *all* cycle statistics including robust variants, and scalar harmonic energy additionally throws away the phase needed to approach that optimum at practical SNR. Anchor/absolute constraints (H^0 gauge fixing) remain the future-spec requirement for view-desync detection.

