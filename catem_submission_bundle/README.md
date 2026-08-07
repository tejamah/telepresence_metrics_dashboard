# CATEM Telepresence 2026 Submission Bundle

Finalized manuscript: **CATEM: A Cross-Layer Measurement and Reporting Framework for Telepresence Evaluation**

- Manuscript version: CATEM prototype v0.2.0
- Format: IEEE conference, US Letter, 10 pt, six pages
- Stable artifact: https://github.com/tejamah/telepresence_metrics_dashboard/tree/v0.2.0

## Which PDF to upload

- If review is anonymous, upload `review_upload/CATEM_Telepresence2026_Review.pdf`.
- If review is identified, upload `identified_upload/CATEM_Telepresence2026_Identified.pdf`.
- Do not upload both manuscript variants.

## Contents

- `review_upload/`: anonymous PDF plus copy-ready portal abstract and candidate keywords.
- `identified_upload/`: identified two-author PDF.
- `source_files/`: minimal reproducible LaTeX source and dashboard figure.
- `artifact_evidence/`: versioned verification results, CATEM specification, DOI audit, and source provenance.
- `administrative/`: author records, declarations, and remaining author actions. These files are not manuscript uploads.
- `CATEM_Telepresence2026_Review_Upload.zip`: review-stage upload package.
- `CATEM_Telepresence2026_Identified_Upload.zip`: identified-PDF upload package.
- `CATEM_Telepresence2026_Source.zip`: minimal compilable source package.
- `CATEM_Telepresence2026_Artifact_Evidence.zip`: optional supplementary evidence package.
- `FILES_MANIFEST.md`: byte sizes and SHA-256 hashes for the packaged deliverables.

## Source build

Run pdfLaTeX twice on `root.tex` for the identified manuscript or twice on `root_blind.tex` for the anonymous manuscript. The source archive intentionally excludes auxiliary files and build logs.

## Before portal submission

Complete the items in `administrative/AUTHOR_ACTIONS.md`, confirm the venue's anonymity policy and page limit, and upload optional artifact evidence only if the venue permits supplementary files.
