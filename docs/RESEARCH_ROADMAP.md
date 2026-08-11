# CATEM Research Roadmap

The current release is a software-verified prototype evaluated with deterministic synthetic fixtures. The separate `validation_v1.py` harness strengthens synthetic ground-truth timing and data-integrity testing, but does not satisfy the real-system technical-validation gate. Research claims advance only through the gated studies in `EMPIRICAL_VALIDATION_PROTOCOL.md`.

## Validation v1 bridge: implemented synthetic ground truth and pipeline traversal

- Replay canonical JSON and CSV exports 100 or more times and compare hashes.
- Recover exact timestamp shifts at `+10`, `+50`, `+100`, `+250`, and `+500 ms`.
- Quantify timing error over 100 three-source event trials.
- Verify controlled missingness, provenance continuity, malformed input detection, mixed sampling rates, and canonical event reconstruction.
- Send 300 events through FastAPI ingestion, declared-offset synchronization, CATEM processing, measurement-contract generation, and JSON/CSV export.
- Verify 10,200 exported measurement records retain timestamps, values, sampling rates, missingness, and provenance.
- Use `CATEM_VALIDATION_V1.md` as the method and ESP32-S3 handoff record.

## Stage 1: content and weighting validity

- Independent multidisciplinary review of layers, metric assignments, metadata, and interpretation boundaries.
- Relevance, clarity, disagreement, and revision reporting.
- Comparison of uniform, task-specific, expert/AHP, Bayesian, and learned weighting only when their evidence requirements are met.

## Stage 2: real-system technical validation

- Integrate a specified VR or telepresence platform, external clock, raw device logs, and controlled network faults.
- Quantify timestamp error, loss, provenance, replay fidelity, stream load, disconnects, and recovery.
- Replace or isolate volatile storage before sensitive or multi-user collection.

## Stage 3: controlled human validation

- Obtain ethics approval and preregister hypotheses, outcomes, exclusions, stopping rules, and sample-size analysis.
- Evaluate construct relationships using validated instruments and synchronized technical measures.
- Preserve original measures and compare every layer or weighting result with a uniform baseline.

## Stage 4: comparative utility

- Compare CATEM with conventional dashboards and single-domain reports.
- Measure interpretation accuracy, consistency, unsupported inference, confidence calibration, time, workload, and auditability.

## Stage 5: prospective field deployment

- Freeze software and configuration for each evaluation period.
- Monitor drift, missingness, false alarms, overrides, incidents, privacy, burden, and maintenance.
- Replicate across platforms, tasks, populations, and institutions before making general claims.

## Required release outputs

- protocol and registration identifier;
- ethics determination;
- versioned software and configuration;
- analysis code and data dictionary;
- permitted de-identified data or a synthetic surrogate;
- deviations, exclusions, adverse events, and complete outcomes; and
- license and persistent archive identifier.

The normalized collection header is provided in `EMPIRICAL_VALIDATION_DATA_TEMPLATE.csv`. Neither file is evidence that a study has been approved or completed.
