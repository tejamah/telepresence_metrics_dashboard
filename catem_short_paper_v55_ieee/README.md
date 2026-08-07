# CATEM IEEE Short Paper Package

This folder is the self-contained IEEE manuscript package for the current CATEM paper revision. The manuscript title has intentionally not been changed pending confirmation of the final agreed title.

## Manuscript files

- `root.tex` and `root.pdf`: identified manuscript source and compiled PDF.
- `root_blind.tex` and `root_blind.pdf`: anonymous wrapper source and compiled PDF.
- `ieeeconf.cls`: IEEE conference class used for both builds.
- `figures/dashboard_overview_full.png`: dashboard figure used by the manuscript.
- `SOURCE_PROVENANCE.md`: revision and evidence provenance.

## Verification evidence

- `verification/verification_results.json` and `.csv`: complete fresh v0.2.0 harness output.
- `verification/table_i_verification.json` and `.csv`: explicit Table I inputs, outputs, fixture hashes, tagged-source checks, and manuscript-match results.

The Table I evidence verifies a latency baseline of 82 ms, timestamp-alignment-error baseline of 3.4 ms, tracking-dropout fault output of 65.5, and eight expected Human State and Cognition records before HRV removal.

## Rebuild and verification

From the repository root:

```powershell
python apps\api\verify_table_i.py
```

From this folder, run pdfLaTeX twice for each manuscript:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error root.tex
pdflatex -interaction=nonstopmode -halt-on-error root.tex
pdflatex -interaction=nonstopmode -halt-on-error root_blind.tex
pdflatex -interaction=nonstopmode -halt-on-error root_blind.tex
```

See `FILES_MANIFEST.md` for SHA-256 hashes of the packaged source, evidence, and PDF deliverables.
