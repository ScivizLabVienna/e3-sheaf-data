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

## Integrity record
Every gate in findings.md pre-registration sections (rounds 6, 8, 10) predates its run; frame-convention ambiguity disclosed and resolved by reporting BOTH faithful readings (E3b); oracle legs are labeled post-hoc diagnostics, never re-gates; E5 spec correction recorded before implementation with no numbers seen. Git: one commit per round, verdict in message (`4dc8a7a` .. `f23d816`).
