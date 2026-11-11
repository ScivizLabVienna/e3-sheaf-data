# E3 roadmap v0.1 -> v0.2 (from PRE_REVIEW.md, 2026-11-10)

Target venue: EM-MIR-style workshop @ MICCAI 2027 (CFPs ~spring '27, subs Apr-Jun '27).
Mode (since 2026-11-10): MANUAL — no cron. Sessions E1/E2/E3 each drive their own project dir only; before any round, read PROJECTS.md + task_plan/findings + this file; commit per round as before; never touch another project's files in-flight.
Backup: EuroVis 2027 short (~mid-Feb '27; VERIFY official dates - third-party calendars disagree).
Visibility (operator 2026-11-11): NO arXiv — workshop-paper level. GitHub + Zenodo DOI suffice. DONE 2026-11-11: v0.2 archived on Zenodo, version DOI 10.5281/zenodo.24138935, concept DOI 10.5281/zenodo.24138934 (record 24138935; files: e3-sheaf-data-v0.2.zip + main.pdf; open access; CC BY 4.0 rights vocabulary + creator "SciVizLab Vienna" + publisher SET IN-PLACE via API same day as a minor update, DOI unchanged). GitHub release body links both DOIs.
Zenodo API recipes (verified 2026-11-11):
- INITIAL deposit: POST https://zenodo.org/api/records with the classic-metadata CANON shape (title/description/publication_date/version/resource_type{id}/creators{person_or_org}/publisher/access_right — that exact shape validates; other/mixed shapes silently drop fields), upload files, publish. Token = access_token embedded in the nativehdc Zenodo webhook config URL on GitHub.
- METADATA FIX on a published record (the license-vocab problem): vocabulary fields live under metadata.rights (NOT "license" — that key is dead input), must be written through the NATIVE serializer: GET/PUT https://zenodo.org/api/records/{id}/draft with header Accept: application/vnd.inveniordm.v1+json, Content-Type: application/json, If-Match: <revision int, no quotes>. rights=[{"id":"cc-by-4.0","title":{"en":...}}] sticks (server resolves + persists the vocabulary). The legacy facade (/api/records PUT) silently drops license/rights but does persist plain fields (description, creators-legacy-shape...).
- FINALIZE: POST https://zenodo.org/api/records/{id}/draft/actions/publish?minor=true (HTTP 202; same recid + same version DOI). Verify on public HTML: cc-by-icon + creativecommons.org/licenses/by/4.0 present.
- Communities cannot be created via token API (scivizlabvienna = 404); community attach skipped, matching nativehdc record.

PUBLICATION POLICY (operator, 2026-11-11 — binding for E3 and any derived/future papers):
1. NO people's names anywhere in the paper (no author individuals, no acknowledgments persons; literature citations unaffected). Author field stays "SciVizLab Vienna" until operator decides at submission time.
2. Non-peer-review disclosure is MANDATORY, verbatim near title/abstract: "This work has not been peer reviewed. It is an output of an autonomous, git-frozen agent research protocol (described in §4) and is published as a preprint for open comment." Apply the same statement to ALL work produced by this campaign method.

Round directives (one per round, cheap first):
1. R25: main.tex rewrites - "View-Gauge Theorem"->Remark; "falsified"->scoped claim; "channel-physics-bound"->"empirically detector-saturated" + caveat sentence (~free).
2. R26: RMS-pruning threshold sweep {1.5..4}xRMS on >=20 tiles, AUROC delta figure.
3. R27+: synthetic deformation field w/ known ground truth as second "stack" (n=1 gap; no new acquisition needed).
4. Later: per-defect-class AUROC breakdown + K-sensitivity {3,6,12} (supplement).

Status: E10 pairwise-QA baseline proxy DONE r24 (baseline tie/loss) = reviewer ask #1 partially met.
