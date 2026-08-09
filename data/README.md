# Sample Data

## Sample Data Notice

`sample_metrics.csv` and `sample_stream_events.jsonl` contain synthetic example records created for software demonstration and verification. Participant identifiers such as `P-101` and `P-102` are fictional and do not represent human research participants or collected human-subject data.

## Artifact Roles

| Artifact | Role |
|---|---|
| [`sample_metrics.csv`](sample_metrics.csv) | Synthetic demonstration dataset for CSV ingestion and dashboard examples |
| [`sample_stream_events.jsonl`](sample_stream_events.jsonl) | Synthetic streaming examples for telemetry-ingestion demonstrations |
| [Canonical object-drop fixture](../docs/catem/catem_specification_v0.2.json) (`event_window_fixture`) | Deterministic five-sample CATEM fixture for event-alignment and measurement-contract verification |
| [Verification results](../docs/catem/verification_results.json) | CATEM v0.2.0 reproducibility evidence produced by the software-verification harness |

These artifacts serve different software-verification purposes. Values in the sample datasets are not expected to match the canonical object-drop fixture, and none of these files contains participant-derived observations.
