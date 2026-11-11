# arXiv bundle manifest (v0.2 FINAL candidate, 2026-11-11) - operator gate applies before upload

## Upload set (tex source submission; total well under arXiv limits)
- paper/tex/main.tex            -- single-file article (booktabs, amsmath, hyperref, xurl, graphicx; no custom .sty/.cls -> arXiv-friendly)
- paper/tex/fig1_mdb.pdf        -- Figure 1 (vector; generated programmatically from committed result .txt artifacts, see repo)
- (main.pdf NOT uploaded; arXiv regenerates. Local compiled copy kept as record.)

## Verify-before-upload checklist
1. tectonic exit 0 + text-layer greps pass (done at v0.2 cut: 'stitcher-free', disk-verified byte counts, Fig/Tab refs resolve).
2. Author list + contact are TODO placeholders -> operator fills before arXiv id request.
3. Repo URL in abstract is public; e12/e13 artifacts not yet pushed (next repo sync) - push before announce.
4. License: recommend CC-BY-4.0 (nativehdc convention; operator confirms).
5. Categories: cs.CV + eess.IV. Zenodo DOI step ordering = operator call (repo already public).

## Backing artifacts (repo, not bundle)
e6..e13 result .txt + src/*.py + e12_{meas,sigma}.npz; findings.md holds every pre-registration dated BEFORE its run (audit trail for referee requests).

## Not included / risks
- SUPPLEMENT.md is markdown prose; if a venue requires in-PDF supplement, ~20-line LaTeX appendix conversion needed (operator call).
- E10 proxy-is-not-the-public-codebase caveat and FIB-SEM sigma-below-floor anomaly are disclosed in main text; no hidden hedges.
