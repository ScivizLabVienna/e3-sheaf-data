# Supplement material (v0.2) - breakdowns, all values parsed from committed artifact .txt files

## S1 View-gauge nullity per channel (N_shift; theory AUROC = 0.500 exactly)
ROI1 GLR (e7_results.txt): 0.500 at every level 0.5-5x. ROI2/FIB-SEM: see e8/e9 N_shift lines (identical structure). E12 synthetic set (known truth): max 0.500 -> the identity doubles as an implementation unit-test (any deviation = gauge broken in code, not in physics).

## S2 K-sensitivity of M_edge AUROC (E13; e13_ksens_results.txt)
K=5: sigma_c (0.74,0.73); AUROC 0.5x..5x = .525/.586/.685/.774/.838. K=7: (0.69,0.77); .522/.575/.697/.756/.840. K=6 real = e6b/e7; synthetic K=6 = e12_synth_results.txt. In units of each channel's own closure sigma the curves coincide within +-0.03: detectability is graph-density invariant (K in 5-7); no K reaches AUROC>=0.9 at <=3x. Absolute px sigma changes with window geometry - one more reason absolute-threshold pruning cannot transfer (S3).

## S3 RMS-prune threshold sweep (E11; e11_results_{roi1,roi2,fibsem}.txt)
tau* (FPR<=0.01) = 2.5 / 2.5 / 3.0; at tau 2-3 recall(<=3x defects) = .53-.74 SBF vs .08-.19 FIB-SEM; tau=1.5 already yields 4.7-12.8% false flags (null RMS underestimates the chi2 tail). Pruning is budget-driven, not rule-driven.

## S4 Known-truth synthetic control (E12; e12_synth_results.txt)
Rigid known translations of real faces, no stitcher in loop: sigma_c 0.85/0.95 px; M_edge AUROC .51/.56/.66/.74/.83 (.5-5x), never >=0.9; N_shift exactly gauge. Saturation is measurement-physics, not stitching artifact; separability caps ~0.83 at 5x even with exact truth.

## S5 Pairwise-QA baseline proxy (E10; e10_results.txt)
EMSIQA/OFSIQA-recipe re-implementation on ROI1: AUROC .42/.34/.38/.53/.67 (.5-5x), i.e. BELOW the sheaf channel at matched relative scale; gate G-E10 not met. Proxy caveat disclosed in main text (not the public codebase run).
