# E-series (E1-E5): detectability of stitching/desync anomalies in registration-style scaffolds
Negative-result study, SciVizLab Vienna, 2026-11. Six frozen one-shot runs; every gate pre-registered in findings.md BEFORE its run; no post-hoc re-gating anywhere.

## Setup
Substrate: k=5-7 view cycles (SciViz microscopy stitching / registration analog). Anomaly classes: rotation-bearing measurement defect on one edge (H^1 carrier); view translation desync (gauge mode in the relative channel). Observables: SE(2) relative poses (P1-frozen law, SIGMA=0.10 m, ROT=0.05 rad) and bearings+compass (E5). Channels tested: sheaf H^1 signed holonomy, gauge-anchored LS residuals (SE(2) and bearing frames), scalar harmonic energy, robust trim-LS, consistency radius.

## Headline result — the MDB-curve thesis
No single detector "sees" or "is blind" to an anomaly class. Every channel is a point on a Baarda minimum-detectable-bias (MDB) curve: AUROC 0.48-0.70 at matched magnitudes for every statistic x observable x class combination tested (n=180-240 each); separation -> ~1 only when |anomaly| >= ~2-3x combined channel noise (E3b rule, confirmed at oracle conditions AUROC 0.999). Reporting one AUROC without the magnitude axis is the error this series documents.

## Stable positive signal
H^1/cycle-consistency on rotation-bearing defects: AUROC .659/.670/.627 replicated across three runs and both observable classes, at the theoretical matched-SNR ceiling ~.63 - i.e. the channel is AT capacity, not broken (CEMP, arXiv:1912.11347, is the theory-level anchor for cycle-consistency outlier information).

## Falsified bets (recorded pre-run, lost cleanly)
- E3b anchor channel at matched SNR (gate .85 -> 0.481/0.488; oracle ceiling 0.572 = information poverty).
- E4 single bad edge no longer pure gauge under anchors (G2 gate .85 -> 0.540).
- E5 bearing observables restore anchor leverage (G1 gate .90 -> 0.599; compass+anchors leave no relative-position redundancy).
- E5 cycle-at-true-angular-magnitude beats SE(2) ceiling (+.05 delta needed -> fell below, small-k single-cycle redundancy).

## Practice consequences (SciViz QC)
1. Natural-magnitude stitching anomalies sit below the MDB of any same-architecture detector -> engineer anchor/anomaly magnitudes >= 3x noise or accept magnitude-targeted specs.
2. Report per-channel MDB curves per anomaly class, never headline AUROC.
3. Cycle/H^1 statistics are worth their cost only for rotation-class defects, where they run at theoretical capacity.



## Real-data validation (E6b, 2026-11-09; EMPIAR-10478 HeLa SBF-SEM, DOI 10.6019/EMPIAR-10478)
On 86 real windows (adjacent lag-10 + wide-baseline global phase-correlation rows; measured triangle-closure sigma = 1.7 px):
- Edge-anomaly AUROC rises monotonically 0.59 -> 0.93 over injections of 0.5-5 x closure-noise: the MDB-curve thesis (claim 2) holds on real measurements; the naive corollary "anomalies near 1-3 sigma are triageable" is FALSIFIED — reliable flagging needs ~4-5 x the measured noise with a plain max-residual detector.
- Rigid one-node desync (view class, all its rows consistently shifted): AUROC exactly 0.500 at every amplitude — the gauge theorem (P1) is not an artifact of synthetic generators; relative content measurements are structurally blind to view-class displacement, at any SNR.
- One instrument defect was caught mid-round by a frame-free fixture (self-referential anchors made the detector exactly flat) and disclosed pre-verdict: E6 first run voided as DGP modeling error, corrected in E6b before any gate result informed a choice.

E7 addendum: swapping the max-abs detector for the GLR-optimal chi2-energy statistic moves AUROC by <= +0.025 at every level (gate still missed at 3x, 0.890) -> the ~4-5x crossing is channel physics (deformation-inflated noise floor), not detector choice. The standard photogrammetry ">2-3x RMS prune" practice is falsified for deformation-dominated channels; it implicitly assumes Gaussian-matched noise with deformation excluded from the scale estimate.

E8 replication: the same frozen pipeline on a SECOND, distant ROI of the block (own closure sigma 1.46 px vs 1.78 px) gives AUROC 0.59->0.93 across 0.5-5x own noise, crossing 0.9 at ~4-5x again - the channel-physics finding is not a one-region artifact. Triangle-closure self-calibration also fails to collapse the curves between regions, i.e. per-ROI noise-scale estimation under deformation is itself approximate: an operational warning for anyone setting prune thresholds from closure statistics.

E9 cross-technique: on pre-registered FIB-SEM muscle (EMPIAR-10070) the closure sigma is ~0.1 px - 15x below the SBF ROIs - and no relative level up to 5x reaches AUROC 0.9 either. Together the three channels show the closure-sigma scale spans two orders of magnitude across techniques while detection always fails at the pre-registered <=3x rule: sigma-multiple thresholds are not transportable; QC needs absolute tolerances set by downstream task, with residuals normalized per-channel only for ranking within a dataset.

E9 data limitation: the FIB-SEM stack's shifts were baked in by NEWSTACK before MRC conversion; the extended header carries only history labels (verified by direct byte read), so no independent true-angle/anchor ground truth exists for this dataset and the E4-style oracle ceiling comparison could not be run there. Absence of ground truth is a property of the archives, not of the method; the two SBF ROIs with usable independent global legs remain the quantitative benchmark.

## Integrity record (updated)
Every gate in findings.md pre-registration sections (rounds 6, 8, 10) predates its run; frame-convention ambiguity disclosed and resolved by reporting BOTH faithful readings (E3b); oracle legs are labeled post-hoc diagnostics, never re-gates; E5 spec correction recorded before implementation with no numbers seen. Git: one commit per round, verdict in message (`4dc8a7a` .. `7052843`).

## E10 pairwise-QA baseline proxy (round 24)

Reviewer-risk closure: EMSIQA/OFSIQA-style masked-mean |diff| pairwise score re-implemented on ROI1 (360 clean pairs), trials mirroring e6b in image domain. Level AUROC {0.5:0.415, 1:0.340, 2:0.375, 3:0.530, 5:0.668}; gate G-E10 not met -> pairwise photometric QA does NOT beat the sheaf channel at matched relative scale (GLR 3x = 0.890 for reference). Caveat disclosed in findings.md (raw-score texture variance; published practice z-normalizes per pair, which changes the frozen statistic). Public-codebase head-to-head remains full-paper scope.

