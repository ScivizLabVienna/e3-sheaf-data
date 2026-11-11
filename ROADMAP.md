# E3 roadmap v0.1 -> v0.2 (from PRE_REVIEW.md, 2026-11-10)

Target venue: EM-MIR-style workshop @ MICCAI 2027 (CFPs ~spring '27, subs Apr-Jun '27).
Mode (since 2026-11-10): MANUAL — no cron. Sessions E1/E2/E3 each drive their own project dir only; before any round, read PROJECTS.md + task_plan/findings + this file; commit per round as before; never touch another project's files in-flight.
Backup: EuroVis 2027 short (~mid-Feb '27; VERIFY official dates - third-party calendars disagree).
Visibility (operator 2026-11-11): NO arXiv — workshop-paper level. GitHub + a Zenodo DOI (mint on the v0.2 release tag; operator's one-time click, pattern = NATIVEHDC doi 10.5281/zenodo.24017023) suffice.

PUBLICATION POLICY (operator, 2026-11-11 — binding for E3 and any derived/future papers):
1. NO people's names anywhere in the paper (no author individuals, no acknowledgments persons; literature citations unaffected). Author field stays "SciVizLab Vienna" until operator decides at submission time.
2. Non-peer-review disclosure is MANDATORY, verbatim near title/abstract: "This work has not been peer reviewed. It is an output of an autonomous, git-frozen agent research protocol (described in §4) and is published as a preprint for open comment." Apply the same statement to ALL work produced by this campaign method.

Round directives (one per round, cheap first):
1. R25: main.tex rewrites - "View-Gauge Theorem"->Remark; "falsified"->scoped claim; "channel-physics-bound"->"empirically detector-saturated" + caveat sentence (~free).
2. R26: RMS-pruning threshold sweep {1.5..4}xRMS on >=20 tiles, AUROC delta figure.
3. R27+: synthetic deformation field w/ known ground truth as second "stack" (n=1 gap; no new acquisition needed).
4. Later: per-defect-class AUROC breakdown + K-sensitivity {3,6,12} (supplement).

Status: E10 pairwise-QA baseline proxy DONE r24 (baseline tie/loss) = reviewer ask #1 partially met.
