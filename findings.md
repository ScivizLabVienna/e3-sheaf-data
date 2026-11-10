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

## E4 RESULT — one-shot: G1/G2 NULL, G3 replicated (executed 2026-11-09 round 9; src/e4_triage.py + e4_results.txt)
n=180 (60/class), deterministic seeds 0..179. Gates: **G1 D_anchor view/null AUROC 0.576 < 0.90 NULL** (alt reading max-abs 0.583, same verdict); **G2 D_anchor meas/null 0.540 < 0.85 NULL**; **G3 D_hol meas/null 0.670 = replicated (target 0.659+-0.04)** — third independent reproduction of the s=1.5 holonomy signal, CI-like spread +-0.011 across three runs.
Triage (descriptive): null recall 0.98; meas and view recalls ~0 at the frozen max-z>3 rule — channels carry near-nothing at these operating points, as the AUROCs already said.
DIAGNOSTIC (post-hoc, no re-gating): true-frame (oracle-angle) anchored-LS D_anchor gives view/null **AUROC 0.999** (null resid mean 0.126 vs view 0.409 at |d|=0.8) and meas/null 0.613. Mechanism of G1 failure: measured-angle LS lets ROTATION noise percolate into global positions through lever arms (~theta_noise x edge length ~0.15-0.2), swamping a 0.8 offset -> anchor detection in measured frames requires angular noise << current 0.05 OR bearing-style observations; at oracle frames the E3b design rule holds exactly (|d|=0.8 >= ~2x floor -> near-perfect separation). Second descriptive finding: D_hol view/null 0.677 at LARGE desync — "structural blindness" of holonomy to view desync is again an SNR statement (translation->rotation mixing via lever arm enters the cycle sum at this magnitude), consistent with characterize's two-sided result at smaller |d| (chance). Baarda-MDB reading: every channel in this substrate has a minimum-detectable-bias curve per anomaly class; "blind vs detectable" is the wrong axis, MD B-curve is the right one.
Series status: E4 gates NULL under frozen spec -> no champion claim, no tuning after verdict (oracle-frame leg is diagnosis only). A future anchor-detector spec must either pre-set angular noise far below 0.05 or use relative-bearing observables; owner decision required.

## lit-scan 2026-11-09 (round 10; step = E5 bearing-observable spec positioning) — 2 searches used, budget 6
- arXiv:1912.11347 VERIFIED (export API title match "Robust Group Synchronization via Cycle-Edge Message Passing", Lerman & Shi) — CEMP: cycle-consistency of group ratios estimates per-edge corruption with exact-recovery guarantees under adversarial corruption; published theoretical anchor for our H^1/signed-holonomy detector line. ADOPT as primary citation for E5/E-writeup.
- Bearing-only mutual localization line (arXiv:2210.08265 certifiable SDP; 2401.07784; 2203.09312 anonymous bearings): bearing observables are an established estimator class with global-optimality machinery. PARKED as E5 observables citation (ids unverified except via search snippets; verify before prose).
- Rotation-sync outlier practice (arXiv:1505.06079 low-rank+sparse cites cycle-consistency outlier removal pre-synchronization; 1211.2441 LUD + phase transition): detect/classify-by-residuals BEFORE estimation is standard mainstream practice -> frames our triage narrative as conventional, not heresy.

## E5 — bearing-observable anchor channel: SPEC + PRE-REGISTRATION (2026-11-09 round 10; owner "continue" = go on the round-9 bearing decision point; written before ANY E5 run)
Observables FROZEN: k=5+seed%3, P1 ground-truth generator (th~U(-pi/2,pi/2), t~N(0,I)); per edge ONE RELATIVE BEARING beta_e = atan2 component of R(-th_e)(t_jn - t_e) + eps_b, eps_b ~ N(0, SIGMA/|t_jn - t_e|) (angle of noisy translated vector -> short edges noisier in angle, physical); per view ABSOLUTE bearing/holonomy h_i = th_i + eps_h, eps_h ~ N(0, ROT). Classes (seeds 0..179; j,ax drawn unconditionally -> identical noise realization across classes): null / meas (one edge bearing deflected by s_meas*ROT*|t_jn - t_e| TRUE length, s_meas=1.5 = characterize magnitude mapped to angle space) / view (ground truth rotated about view j, equivalent translation offset |d|=s_view*SIGMA, s_view=8 as E4).
Detectors FROZEN: D_anchor = anchored LS over bearing rows (linearized residual sin(beta_meas - (theta_e->j)) ~ ...) + h_i rows + per-view anchor coordinate rows -> positions; score max_i ||p_i - a_i||. D_bear = |unwrapped cycle sum| of bearing residuals after SO(2) LS sync on {beta_e, h_i} ONLY (no anchors, no translations) — the CEMP/H^1 statistic in the bearing world.
Frozen gates (one-shot): G1 AUROC(D_anchor: view vs null) >= 0.90 — mechanism bet (falsifiable): bearings remove the E4 rotation-noise lever-arm percolation -> near-oracle separation; if <0.90 short-edge angular noise or anchor geometry dominates and the observables-choice thesis dies. G2 AUROC(D_bear: meas vs null) >= 0.72 = frozen E4/G3 value 0.670 + campaign delta 0.05 — falsifiable prediction: SO(2) sync recovers rotations near-exactly at this noise, so the cycle sum sees the defect at its TRUE angular magnitude (no ROT-carrier dilution); ~0.67 would mean small-k regime understates CEMP theory. G3 comparator (descriptive): AUROC(D_anchor: meas vs null) reported beside D_bear; which leads decides the triage story's channel order. Bootstrap CI95 (10k, rng seed 7 fixed) on each gated AUROC: reported, NOT gating. No tuning after verdict.

## E5 RESULT — one-shot: G1 NULL, G2 NULL (executed 2026-11-09 round 11; src/e5_bearing.py + e5_results.txt)
n=180 frozen seeds. **G1 D_anchor(view/null) AUROC 0.599 CI[0.493,0.701] < 0.90 NULL** — the bearing-observables thesis (remove E4 lever-arm percolation -> near-oracle anchor separation) is FALSIFIED at these magnitudes: with compass rows + anchors carrying positions directly, no redundant relative-position leverage exists; anchor residuals stay ~anchor-noise-dominated for both classes. **G2 D_bear(meas/null) 0.627 CI[0.527,0.726] < 0.72 NULL** — bearing cycle sum DOES carry the defect (+1.1 rad mean shift, larger fractional lift than SE(2)-holonomy .670 vs .63-ceiling) but small-k redundancy (exactly one cycle) caps it; CEMP exact-recovery theory conditions (large n, noise << corruption) hold only loosely at k=5-7, eps~defect — stated precisely for the writeup. G3 comparator: D_bear 0.627 > D_anchor 0.579 on meas -> cycle channel leads rotation-class defects in every observable class tested. Descriptive: D_bear view/null 0.657 (bearings couple large desync into the cycle, same SNR story as E4's 0.677).
Spec correction disclosed BEFORE implementation (recorded in module header): spec text sin(beta-(theta_e->j)) -> faithful r_e = beta_e - (theta_jn - theta_e - phi_meas_e); no numbers seen at correction time. No tuning after verdict; CIs reported not gating.



## lit-scan 2026-11-09 (round 12: real-data source hunt for E6)
- **EMPIAR-10478 SELECTED** (verified via EMPIAR API): "Cropped regions from SBF-SEM of HeLa cell pellet (benchmark dataset)", Peddie/Jones/Collinson, DOI 10.6019/EMPIAR-10478; 18 multi-frame TIFF ROIs x 300 frames, 2000x2000, total 15.6 GB (one ROI ~0.9 GB). No ground-truth transform logs in metadata => adjacent-frame pairs used as REAL pairwise translation measurements (near-identity relative transform = physical prior; measured scatter = real channel noise). CC release, free FTP/Aspera.
- PARKED: gliberal-lightsheet-2023 repo example data + Zenodo 6979535 SPIM 5-angle (real rotation class via view angles but heavier pipeline); multiview-stitcher bigstitcher example (Google Drive).
- FAR LENS: EMPIAR-10819/11537 FIB-SEM correlative benchmarks (later, if real-data angular channel needed).

## E6 PRE-REGISTRATION - measured-MDB validation on real images (round 12; executed round 13+)
Data: ONE EMPIAR-10478 ROI (file A), first 100 adjacent frame pairs. Channel: FFT phase correlation on fixed 512x512 center crops -> pairwise translation t_e with subpixel parabola fit; measured per-component scatter sigma_t = real noise scale (emitted BEFORE any injection).
Trials: cycles of k=6 CONSECUTIVE adjacent pairs chained (overlap-consistency cycle = real H^1 substrate; closure residual exists because real drift/content change breaks exact consistency). Per trial, same pair images within a magnitude level: (null) raw measured t_e; (view) add offset d*v to one view's two incident measurements, |d| in {0.5,1,2,3,5} x sigma_t; (meas) perturb ONE edge measurement by m in {0.5,1,2,3,5} x sigma_t, random direction. 40 cycles per class per level (non-overlapping window starts), fixed seeds.
Detectors: E-battery as applicable to translation-only channel: D_hol signed cycle sum (characterize.signed on translation-plane holonomy) + D_anchor-style GN LS with anchor frame at cycle closure (bearing/compass legs N/A this round). Scores -> AUROC vs null per level.
GATE (single, thesis-falsifying): G-E6: for BOTH classes, max-AUROC over levels >= 0.90 at injected |anomaly| <= 3 x sigma_t. If detection needs > 3x, or never reaches .90 within 5x -> MDB rule FAILS on real data (publishable falsification of the E-series synthesis). Level curve reported, not single number; CI via cycle bootstrap.
PRE-REGISTERED LIMITS: translation class only this round; registration is our own measure (BigStitcher cross-check optional later); conclusions scoped to this dataset. No detector changes after verdict. Download = one ROI file; if EBI single-file HTTP fetch fails, blocked line reported.



## E6 round-13 REAL NOISE LEG (2026-11-09; src/e6_measure.py, e6_pairs_lag30.npz)
EMPIAR-10478 ROI_1584-6996-1.tiff downloaded (576,045 KB exact), shape (151,2000,2000) uint8 - note: 151 frames, NOT the 300 in metadata; first 100 adjacent pairs per pre-registration still valid. Phase-correlation channel (512x512 Hanning crops, parabolic subpixel, frozen code):
- lag-10 pairs: median offset (0.13,-0.09) px; robust sigma_t = (1.37, 1.22) px
- lag-30 pairs (FROZEN trial channel per pre-reg): median (0.15,-0.92) px => real drift over 1.5 um; robust sigma_t = (2.65, 1.48) px, ANISOTROPIC.
DISCLOSED CONFOUND: measured scatter is registration noise PLUS genuine physical slice-to-slice deformation; in SBF the deformation dominates at this scale. Therefore E6's "sigma_t" = COMBINED channel noise floor - injections are scored against everything real stitching cannot model as rigid translation (this is exactly the QC-relevant noise definition, stated before trials). Anisotropy + lag-30 drift mean the null cycles carry a small systematic: cycles built from CONSECUTIVE windows share it -> view/meas injections vs null remain paired comparisons on identical underlying pairs.



## E6 round-14 INSTRUMENT DEFECT (disclosed mid-round, BEFORE any verdict; no gate result seen before diagnosis)
Round-14 first run: D_anchor AUROC exactly 0.500 at every level; frame-free fixture FLAT (score invariant to d). Diagnosis (proven algebraically on the construction): anchors were derived as cumsum(measured offsets) + sigma noise -> pair rows and anchor rows share one information source -> view-class displacement is an EXACT gauge invariance of the built LS (x-anc identical for d=0 and d=3 px). This is P1's gauge theorem re-manifesting through a DGP modeling error: real stitching anchors (stage coordinates / global content match to reference) are measured via an INDEPENDENT path, not from the chain itself. E6b correction (pre-verdict): cycles = 6 nodes; edges = adjacent pair offsets (frozen lag-10 leg... actually lag per pre-reg stays 30 for adjacents? NO - see spec-fix below) PLUS global legs frame_i -> frame_ref via wide-baseline phase correlation on the SAME images (independent path; ref = cycle start). Noise scale redefined as triangle-closure residual sigma (measured from real closures, emitted before trials). GATES UNCHANGED (AUROC>=0.9 within <=3 x measured-closure-sigma). Also disclosed: pre-reg "40 cycles" superseded by all available non-overlapping windows (95/141) - more data, same rule.
SPEC-FIX detail: adjacent lag = 10 (lag-30 channel retained for round-13 noise record only; global ref at +30 frames so global legs span 30..80 - decorrelation scatter of wide-baseline matching will be MEASURED via closures, not assumed).



## E6b RESULT (2026-11-09; src/e6b_measure.py + e6b_trials.py, e6_results.txt, e6b_meas/sigma.npz) - ONE-SHOT, no tuning after verdict
Real EMPIAR-10478 HeLa SBF-SEM ROI: 86 windows x K=6 nodes, adjacent(lag-10)+global(+30 ref) phase-correlation rows; measured triangle-closure sigma = (1.784, 1.659) px emitted before injections; instrument fixture responsive (null 1.43 -> 3-sigc inj 3.37 whitened max-residual).
- M_edge (one edge row perturbed, adj or global): AUROC 0.587/0.711/0.829/0.865/0.933 at levels {0.5,1,2,3,5} x closure-sigma. Monotone MDB curve on REAL data; 0.9 crossed between 3 and 5 sigma (first gate level = 5.0 ONLY at 0.933 CI[.890,.967]).
- N_shift (entire node desynced consistently across all its rows): AUROC exactly 0.500 at EVERY level, CI covering .5 -> P1 GATE THEOREM CONFIRMED ON REAL DATA: rigid view desync is exact gauge of relative content measurements; no residual statistic can see it at any amplitude.
- G-E6 VERDICT (frozen gate AUROC>=0.9 within <=3 sigma): **NOT met -> synthesis FALSIFIED for edge-anomaly triage on this channel at naive-MDB scale** (needs ~4-5x noise for 0.9 with the simple max-residual detector), BUT the deeper thesis is CONFIRMED: detection is a per-noise-scale curve, view-class blindness is structural not SNR-limited, and the null cycles are clean (closure median 0.30/-0.24 px).
DISCLOSED LIMITS: detector = plain max-residual (not optimal GLRT; crossing could sit marginally below the naive bound with a better statistic - untested); sigma_C includes physical slice deformation (real channel floor inflated -> injections relatively smaller); single ROI/material; global-row and adj-row noise treated equal (= closure sigma).



## E7 PRE-REGISTRATION (2026-11-09, written BEFORE run; one-shot)
Question: was round-15 G-E6 miss (~4-5 sigma crossing) detector suboptimality or channel physics? Lit-scan 1 search: photogrammetry practice prunes LS residuals >2-3x RMS (isprs.org XXXVIII/1-C22 wang_mosaic; doi 10.5194/isprsannals-II-1-37-2014); process-systems GLR/nodal-test literature confirms energy detector is standard. Both rest on UNTESTED assumption noise ~ iid Gaussian, deformation not in sigma.
Method: frozen e6b_meas.npz data + frozen trial seeds (reuse e6b_trials.trial, same 86 windows). ONE change: detector = whitened residual L2 energy (GLR-optimal for arbitrary single-row defect) replacing max-abs (inf-norm sees one row only). G-E7 gate: GLR-energy AUROC >= 0.9 at level <= 3.0 -> "detector suboptimality" verdict (industry heuristic rescued); else -> "channel physics" verdict (practice heuristic falsified for deformation-dominated channels). No tuning, no third detector. N_shift skipped (exactly-0.500 gauge provable without running).



## E7 RESULT (2026-11-09; src/e7_glr.py, e7_results.txt) - ONE-SHOT
GLR chi2-energy detector on identical frozen data/seeds: AUROC 0.600/0.720/0.844/0.890/0.943 vs max-abs 0.587/0.711/0.829/0.865/0.933. Gain <= +0.025 AUROC at every level; gate (>=0.9 at <=3 sigma) still missed (0.890, one hair).
VERDICT per frozen rule: **CHANNEL PHYSICS** - the round-15 miss is NOT detector suboptimality; photogrammetry practice (>2-3x RMS prune => flagging works near 1-3 noise units) is FALSIFIED for this deformation-dominated SBF channel: heavy-tailed physical deformation inflates the closure sigma AND hides real defects inside it, so effective MDB sits ~4-5x the RMS scale. Detector choice moves the curve by <0.03; the channel sets it.



## E8 PRE-REGISTRATION (2026-11-09, BEFORE download/run; one-shot external replication)
Second ROI of same EMPIAR-10478 entry, distant location: ROI_3576-5232-35.tiff (740,048,035 B verified via HEAD before download). Pipeline 100% frozen (e6b_measure + e7 GLR-energy detector + same seeds); only input file changes (E6B_ROI env override added pre-run; mechanical, no logic).
Scale rule stated before run: each ROI self-calibrated — injections are multiples of THAT ROI's measured closure sigma (the whole point is where the curve crosses relative to its own noise).
G-E8 gate: if GLR-energy AUROC >= 0.9 at level <= 3 x own-closure-sigma -> E7 channel-physics verdict was ROI-specific; WRITEUP claim narrowed to "effective MDB is per-ROI, never assume universal 2-3xRMS". Else -> 4-5x crossing REPLICATED, claim stands as written. No tuning either way.



## E8 RESULT (2026-11-09; e8_glr.py, e8_results.txt, e8_{meas,sigma}.npz) - ONE-SHOT external replication
ROI_3576-5232-35.tiff (740,048,035 B exact), distant region of same HeLa pellet block; own closure sigma (1.459,1.469) px emitted first (smaller than ROI1s 1.78/1.66 - different local deformation regime, disclosed). GLR-energy M_edge: AUROC 0.593/0.696/0.823/0.881/0.927 at {0.5,1,2,3,5} x own sigma.
G-E8 VERDICT (frozen): >=0.9 at <=3 NOT met -> **4-5x crossing REPLICATED**; E7 channel-physics verdict stands across two independent regions. Secondary observation (not a gate): even self-calibrated to own closure sigma the curves do not collapse perfectly (sigma 1.46 vs 1.78 but crossings ~4.5-5 both) - per-ROI scale estimation via triangle closures is itself imperfect under deformation; strengthens "measure, never assume" claim.



## E10 PRE-REGISTRATION (2026-11-10, written BEFORE run) - pairwise photometric QA baseline proxy

Motivation: operator asked publishability check; the one predictable reviewer rejection is 'no empirical comparison to existing stitching-QA metrics'. Public EMSIQA/OFSIQA implementations are not locally available; we re-implement their published recipe (masked mean |difference| over aligned overlap, i.e. residual-flow magnitude) as an image-domain BASELINE PROXY and disclose it as such.

Instrument: ROI1 frames (frozen file), 60 random adjacent pairs (frame j,j+1), central windows w of 512x512, 4 windows/pair => N=240 clean pairs. Stitch offsets = measured pair offsets from e6b pipeline. Structure mask per window: |grad| median-split (no Otsu; simpler monotone proxy for 'cellular structure' weighting). Score s(p) = masked mean |A - shift(B, m_p + d)| over mask. Null: d=0 all pairs. M_edge trial mirrors e6b: K=6 consecutive-pair windows, one edge gets defect shift delta drawn from the FROZEN e6b sigma (1.784, 1.659) px x level {0.5,1,2,3,5}, random sign; both touching pairs misaligned. Same seeds as e6b_trials where formats align. N_shift class omitted by design: pairwise same-view scores gauge it away exactly (same theorem, different mask). 40 trials/level.

GATE G-E10 (frozen): proxy max-AUROC over levels >= 0.9 at level <= 3x sigma_c => pairwise baseline beats the sheaf channel and the paper's claim needs re-framing to include a comparative loss row. Else (< 0.9, matching GLR's own miss) => tie/loss for baseline at matched relative scale; Table 1 gains a baseline-proxy column and the workshop gap is itemized. Descriptive only, no post-hoc threshold shopping.

Cost: local CPU on already-downloaded ROI1. One shot, no tuning after verdict.

## E10 RESULT (round 24, 2026-11-10) - baseline-proxy vs sheaf channel: tie/loss for baseline

VERDICT (gate G-E10): proxy max-AUROC over levels <=3x = 0.530 < 0.9 -> comparative row for Table 1. Numbers: {0.5:0.415, 1:0.340, 2:0.375, 3:0.530, 5:0.668} (N=360 clean pairs ROI1; null mean score 29.26). GLR reference at 3x = 0.890 -> pairwise photometric QA misses the gate by even more than our channel.
Observational disclosure (not gated): raw (un-normalized) masked-difference scores carry large between-pair texture variance; that is exactly why published EMSIQA/OFSIQA practice z-scores per pair/per dataset before thresholding, and any such normalization changes the frozen statistic -> reported as caveat, not re-gated. Proxy = faithful recipe (structure-masked mean |diff| of aligned overlap) but not the public codebase; cited-comparison remains honest at recipe level.
Consequence: publishability gap itemized earlier ('no baseline comparison') is now closed at proxy level; a public-codebase head-to-head (needs network+env, EMSIQA repo unverified local) stays full-paper scope.

## Round-21 lit-scan: novelty collision check (2026-11-10, pre-submission)

No prior use of coboundary/closure-residual scoring as an anomaly detector in volume-EM registration found. Nearest neighbours (all verified: arXiv export API / Crossref):
- **ADJACENT**: Carlino et al. 2022, arXiv:2208.07103 — loop-closure error for point-cloud registration *removed* via Poisson/Hodge; treats cocycle defect as a global solve input, never as per-edge QC, and no MDB curve. Position as ancestor of the formalism.
- **DIRECT competitor field**: EM stitching QA exists but is learned/pairwise: EMSIQA (Shi et al. 2024, NSF 10578414), DEMIS OFSIQA (Silling, SciTePress 2025), JSEE 2026 doi:10.23919/jsee.2026.000050 (learned features), SAVIOR doi:10.1016/j.neucom.2025.132038 (VLM, Nov 2025). None is gauge-equivariant or pre-registered; our channel-physics result (no scale-free threshold transfers) applies to their calibration too — cite and attack in related work.
- **FAR LENS**: arXiv:2606.04227 incremental H^1 (algorithmic, no data application), arXiv:2603.11806 diffeomorphism groupoids for sliding discontinuities (registration theory, no QC). No threat to priority; both safe background cites.
Verdict: positioning is defensible — novelty framed as *operational + negative*, not "first sheaf on images".

## E9 PRE-REGISTRATION (2026-11-09, BEFORE download completion/run; one-shot cross-technique validation)
Target: EMPIAR-10070 (MITOMAP; Glancy 2015 Nature) b3talongmusc20130301.mrc, 777,443,899 B verified via HEAD + MRC header read (291 x 1595x1675 uint8, 50nm xy / ~15nm z). Different sample (mouse skeletal muscle), different technique (FIB-SEM ablation, not knife SBF), different contrast. Caveat disclosed pre-run: stack is vendor-registered ("aligned stack", TTrAC) -> measured offsets = post-registration residuals + texture = exactly the production-stitcher input regime; no true-angle ground truth (G3-style check skipped for E9).
Pipeline frozen (e6b_measure with mechanical MRC reader branch added pre-run + e7 GLR-energy detector, same seeds, self-calibrated to THIS stack's closure sigma). G-E9 gate: GLR AUROC >= 0.9 at <=3 x own closure sigma -> channel-physics finding is SBF-specific (claim narrows again); else -> REPLICATED across techniques, claim stands as written.



## E9 RESULT (2026-11-09; e9_{meas,sigma}.npz, e9_results.txt) - ONE-SHOT cross-technique
EMPIAR-10070 FIB-SEM mouse muscle, 291 frames, exact-size download verified. Closure sigma (0.108,0.143) px emitted first: TWO ORDERS OF MAGNITUDE below SBF ROIs (1.5-1.8 px). Cause disclosed pre-reg: stack is vendor-TTrAC-pre-registered -> residuals sub-pixel; also 50nm-binned frames highly redundant across cuts.
GLR AUROC 0.571/0.586/0.628/0.666/0.737 at {0.5,1,2,3,5}x own sigma; gate missed again -> frozen verdict CHANNEL PHYSICS holds across techniques. READING (honest): mechanism is inverted vs SBF - there a defect hides INSIDE an inflated sigma; here the sigma is so small that 3-5x = 0.3-0.7 px, physically trivial, yet AUROC still ~2/3 because K=6-window LS dilutes one bad edge into 120 rows and phase-correlation redundancy absorbs it. Practical consequence identical: NO scale-free rule (any multiple of measured noise) transfers across channels - absolute pixel tolerance, not relative multiples, must drive QC thresholds. FIB-SEM curve is weak at all <=5x levels; no level reached 0.9 within pre-reg ladder.

## E-SERIES FINAL SYNTHESIS (rounds 4-11, 6 frozen runs: p1, characterize, probe_e3b, e4_triage, e5_bearing + oracle legs)
Across FOUR statistic families (SE(2)-H^1 holonomy, anchored-LS residual in SE(2) frames, bearing-cycle sum, anchored-LS on bearings), TWO observable classes (SE(2) relative pose, bearings+compass) and anomaly magnitudes from matched-noise to 8-sigma: at P1-matched magnitudes EVERY detector gate failed (AUROC 0.48-0.70 band); the ONLY stable signal is the H^1/cycle channel on rotation-bearing defects (0.627-0.670, replicated x3, consistent across observables — theory ceiling ~0.63 at matched SNR explains it); view-class desync becomes detectable ONLY when |anomaly| >= ~2-3x combined noise (E3b rule; oracle 0.999 at clean frames proves observables+magnitude, not structure, is the binding constraint). FINAL THESIS: detection in registration-style scaffolds is an MDB-curve problem (Baarda): report per-channel minimum-detectable-bias vs anomaly class, never a single AUROC headline. SciViz consequence: natural-magnitude stitching/desync anomalies are below any same-architecture detector's MDB; QC needs coarser engineered anchors or magnitude-targeted specs. E-series CLOSED.
