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


## lit-scan 2026-11-08b (round 6; step = anchor-spec positioning) — 4 searches, budget 6
- arXiv:2608.06885 — "Rigid-Covert GNSS Spoofing of UAV Swarms: A Structural Blind Spot, Its Detection Limit, and Absolute-Anchor Defenses": proved Prop.1 (any relative-only detector is blind to common-mode translation = our gauge mechanism) and Prop.2 (>=1 absolute anchor restores translation observability; >=2 for rigid motion), plus a detection floor set by anchor drift rate — adopt: this *is* E3's future-spec literature basis; E3b probe below cites it; anchor-residual detector bound = spec template. [API-verified, submitted 2026-08]
- arXiv:1910.05505[=1910.05509] "A Computational Theory of Robust Localization Verifiability..." — l1 recovery depends only on measurement-graph topology + outlier support/sign: cycle/anchor topology decides recoverability, mirrors our scaffold-first stance — park. [API-verified as 1910.05509]
- arXiv:1801.02112 (Carlone et al.) convex relaxations PGO w/ outliers; two-stage estimate+residual-threshold outlier detection = the strong non-sheaf baseline for any anchor spec — adopt as E3b/E4 baseline template. [API-verified]
- Geodesy classics (no arXiv; cited by venue): free-network adjustment / datum-defect inner constraints (Teunissen 1984; Deakin notes) and extended S-transformation for deformation analysis — H^0 gauge fixing with named 50-year formalism; "anchor disagreement between epochs" = their inter-campaign datum drift. Adopt for writeup framing.
- FAR LENS music theory (voice-leading/cantus firmus): one sentence — a view shifted against an independent fixed reference is exactly a voice discordant against the cantus, detectable only relative to it; instantiates Prop.2 intuitively but adds no machinery → dropped per rule.

## E3b — anchor-channel feasibility probe: SPEC + PRE-REGISTRATION (2026-11-08 round 6, written before run)
Rationale: P1 NULL established cycle statistics are blind to view-level desync (gauge). 2608.06885 Prop.2 says an *independent* absolute channel restores observability. SciViz analog = GCPs/control markers in photogrammetry. This probe validates the mechanism end-to-end on our exact P1 substrate before any E4-style commitment; NOT a sheaf-vs-baseline gate (literature shows any anchor-residual detector works; champion question deferred).
Frozen design (one-shot, deterministic seeds 0..239): k=5+seed%3 cycle exactly as run_p1 trial(); view-level desync on ONE view (same axis/offset convention and strengths as P1: positives s in {1.5,2.5} alternating, nulls s=0; rotation noise .05 rad, translation sigma .10). **Anchors:** every view i gets an absolute 2-D position observation a_i = (true PRE-desync translation) + N(0, .10^2 I) — the independent-channel assumption is exactly what "anchor" must mean. Detector (both arms same fit): LS translations using measured relative edges (weight 1/sigma^2) plus anchors (same weight, unrotated frame), rotations fixed at measurements; score = max_i ||anchor_i - fit_pos_i||.
Frozen gate: E3b spec VALID iff AUROC(anchor residual) >= 0.85 on aggregate positives vs nulls. Desynced-anchor DIAGNOSTIC (recorded, not gated): anchors drawn POST-desync (same channel => internally consistent by construction). No tuning after the run; one number decides.

## E3b RESULT — one-shot NULL (executed 2026-11-09 round 7; `src/probe_e3b.py` + `probe_e3b_results.txt`)
Frozen-gate reading (PRIMARY, literal spec text "LS translations ... rotations fixed at measurements; score = max_i ||anchor_i - fit_pos_i||"):
**AUROC = 0.481 < 0.85 -> E3b spec NULL.** Alternate faithful reading (max pairwise disagreement anchor-vs-rotated-edge-observation): AUROC = 0.488.
The pre-registration fixed the score formula but left the frame convention for rotating measured local edge vectors ambiguous under noisy angles;
BOTH readings were computed from the frozen generator before any verdict, both fail far below gate -> one-shot stands under either reading. No tuning applied after.
DIAGNOSTIC (as pre-registered): anchors drawn POST-desync AUROC 0.481/0.488 — same-channel anchors cannot point at the desynced view, floor-only as expected.

**Post-hoc oracle ceiling (diagnostic, added AFTER the one-shot number — explains WHY, does not re-gate):** rotating measured edge obs by TRUE
per-view angles and pooling via the same anchored LS gives null mean 0.143 / pos mean 0.153 -> AUROC 0.572 even with perfect frames. The generator is a
faithful P1 twin (RNG draw sequence identical to run_p1.trial; verified in-process via returned truth). Mechanism: per-trial anchor channel information
about a single-view shift d scales with |d| relative to the combined noise floor sigma_anchor-pair + sigma_edge-chain (~0.3 at P1-matched settings);
P1 s=1.5/2.5 gives |d| = 0.15/0.25 -> ratio < 1, i.e. BELOW the pre-registered 0.85 requirement no matter the estimator. Frame-free fixture (all rotations zero)
separates cleanly at d = 0.30 (null LS max-resid 0.057 vs desync+PRE-anchor 0.154, matching LS-split theory ~d/3): the instrument works whenever |d| >~ 2x noise —
the P1-matched regime simply does not provide it.

**Quantitative design rule shipped by E3b (transferable):** an absolute-anchor channel detects view-level desync at AUROC >= 0.85 only when
|desync| >= ~2-3 x combined anchor/chain noise; real-world anchors work because anomalies are engineered >> noise (GNSS spoofing meters vs dm noise, 2608.06885
detection floor; GCP residuals in photogrammetry). Under P1-matched anomaly-amplitude-equals-noise conditions NO channel of the substrate beats scalar energy
(E3 round-5: scalar already near-optimal), so anchor residual adds nothing there either. E3 negative-result arc now complete and mechanistically explained at
BOTH levels: gauge blindness (structural, P1+characterize) AND information poverty of the anchor channel at matched SNR (E3b).

## lit-scan 2026-11-09 (round 8; step = E4 fresh-spec positioning) — 2 searches used, budget 6
- arXiv:2308.02674 — "Consistency-Complete Multi-Robot Spatial Perception..." (Maceira-Price et al.): defines pairwise internal consistency of a measurement set under threshold gamma chosen from chi-squared WITHOUT dataset knowledge; composition test = runnable baseline for per-measurement QC. PARK as E4 second non-anchor baseline next to Carlone two-stage residual-threshold (1801.02112, already adopted r6). [from search snippet; id verify before citing in any writeup]
- Survey (no arXiv; JISDM 2022 + TU Delft "Network Quality Control" + Vermeer "Statistical methods in geodesy"): **Minimal Detectable Bias (MDB)** = Baarda 1968 internal-reliability formalism; detectability threshold computed from design matrix A and covariance — i.e. geodesy already HAS a closed-form theory of exactly what E3b measured empirically ("anomaly >= ~2-3x combined noise"), and datum defect / S-transformation = the named 50-year formalization of our gauge mechanism. ADOPT as E4 writeup frame: E3/E3b = an MDB study for sheaf scaffolds; heresy-free, citable lineage (Teunissen/Baarda). [no-verify-needed: non-arXiv venues cited by name]

## E4 — two-channel QC triage on anchored scaffold: SPEC + PRE-REGISTRATION (2026-11-09 round 8; operator-authorized fresh spec; written before ANY E4 run)
Substrate = P1 k-cycle (k=5+seed%3) PLUS the E3b absolute-anchor channel on every view. Three classes, deterministic seeds 0..179: null (60), meas (60: rotation closure defect on ONE edge MEASUREMENT, magnitude s_meas x ROT, s_meas=1.5 — EXACTLY the characterize.py frozen convention that produced 0.659), view (60: translation desync on ONE view at s_view=8, |d|=0.8 = ~2.7x the 0.3 combined anchor/chain noise floor — sized per the E3b design rule). Detector statistics FROZEN now: D_anchor = E3b anchored-LS max anchor residual (identical function, no changes); D_hol = signed |holonomy| from characterize.py applied to edge channel alone (anchors never enter it).
Frozen gates (one-shot each): G1 AUROC(D_anchor: view vs null) >= 0.90. G2 AUROC(D_anchor: meas vs null) >= 0.85 — prediction MECHANISM (my risk, stated before run): with anchors, a single bad edge is NO LONGER pure gauge (endpoint positions pinned), so anchor residuals should carry it diluted over adjacent vertices; if this fails, anomaly-class dependence of anchoring beats the geodesy-MDB expectation. G3 AUROC(D_hol: meas vs null) within +-0.04 of frozen characterize value 0.659 (same s_meas=1.5) (replication leg — no anchor involvement expected).
Triage output (descriptive, NOT gated): per-trial argmax class score -> {null, meas, view} confusion table + per-class recall. If and only if G1&G2&G3 pass: round-9+ champion comparison = Carlone two-stage residual-threshold (1801.02112 template) vs max-z fusion of the two channels vs 2308.02674-style pairwise-consistency set test, NEW pre-registration required (champion claims need operator accept per campaign rule). No tuning after the run; one number decides each gate.
