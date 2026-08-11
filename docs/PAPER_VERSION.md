# CATEM Paper Version and Evidence Baseline

## Manuscript metadata

| Field | Value |
|---|---|
| Title | CATEM: A Timestamp-Aware Cross-Layer Framework for Telepresence Evaluation |
| Authors | Teja Maheshwara and Sara Falcone |
| Affiliation | Seidenberg School of Computer Science and Information Systems, Pace University, New York, NY, USA |
| Venue | 2026 IEEE Conference on Telepresence |
| Manuscript | 82 |
| Status | Submitted; received August 8, 2026 |
| Software version named in the paper | CATEM v0.2.0 |

This record mirrors the metadata in the submitted six-page review manuscript. The review PDF is marked confidential and is therefore not stored in this public repository.

## Evidence reported in the submitted paper

The manuscript reports the bounded CATEM v0.2.0 software-verification result represented by:

- `apps/api/verification.py`;
- `docs/catem/verification_results.json`;
- `docs/catem/catem_specification_v0.2.json`; and
- the canonical 35-record object-drop event fixture.

The committed reference artifact records:

- 17 of 17 functional, reproducibility, and fault-injection checks passing;
- three identical deterministic replays;
- two authored synthetic session summaries;
- five object-drop samples at offsets `-2`, `-1`, `0`, `+1`, and `+2 s`;
- 35 traceable event-window source records; and
- independently applied latency, HRV-removal, timestamp-error, and tracking-dropout conditions.

These are authored synthetic software-verification results. As stated in the paper, they support measurement-contract conformance and transparent implementation behavior. They do not establish construct validity, predictive performance, researcher utility, causal relationships, hardware timing accuracy, human effectiveness, or production readiness.

## Post-submission extensions on `main`

The following results were added after the manuscript was received and must not be described as results reported in the submitted paper:

| Extension | Result | Scope |
|---|---:|---|
| CATEM Validation v1 | 39/39 checks | Helper-level deterministic synthetic timing, missingness, provenance, input quality, export replay, and canonical event reconstruction |
| CATEM end-to-end pipeline validation | 33/33 checks | In-process FastAPI ingestion, declared-offset synchronization, CATEM processing, measurement-contract generation, and JSON/CSV export |

The post-submission suites strengthen software evidence but remain synthetic. They do not replace the planned ESP32-S3 hardware-in-the-loop study, expert evaluation, or human-subject validation.

## Versioning rule

When describing the submitted paper, cite only the v0.2.0 evidence baseline above. When describing the current repository, identify the 39-check and 33-check suites as post-submission validation extensions and preserve their interpretation boundaries. Future accepted-paper metadata, DOI, proceedings pages, or citation text should be added only after they are confirmed by the venue.
