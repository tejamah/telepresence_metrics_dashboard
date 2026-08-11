# CATEM Validation v1

Status: deterministic synthetic ground-truth validation implemented; hardware-in-the-loop phase not yet executed
Software target: CATEM 0.2.0

## Purpose and evidence boundary

CATEM Validation v1 tests whether the software preserves and reconstructs known evidence correctly. It does not test whether prototype transforms, thresholds, layer summaries, or weights are psychologically or scientifically valid.

The committed reference run establishes deterministic behavior for authored timing, missingness, provenance, input-quality, export, and event-window fixtures. It does not establish hardware synchronization accuracy, construct validity, ecological validity, causal validity, predictive accuracy, human-subject effectiveness, or production readiness.

## Reproduce the reference run

From the repository root:

```bash
cd apps/api
python validation_v1.py
```

Defaults:

- 100 JSON and CSV replays;
- 100 ground-truth event trials;
- three streams per trial: network, tracking, and sensor;
- source offsets of `+20 ms`, `+45 ms`, and `+12 ms`;
- deterministic residual error pattern of `-2`, `-1`, `0`, `+1`, and `+2 ms`;
- exact-shift cases at `+10`, `+50`, `+100`, `+250`, and `+500 ms`; and
- missingness cases at `0%`, `5%`, `10%`, `25%`, and `50%`.

The command exits nonzero when any check fails and writes:

- `docs/catem/validation_v1_results.json`
- `docs/catem/validation_v1_results.csv`

Use `--replays`, `--trials`, and `--output-dir` to change the run configuration. Replay and trial counts must each be at least 100.

## Reference results

The reference run contains 39 checks. The quantitative timing output is calculated over 300 aligned observations. Because the residual pattern is authored, the expected results are exact:

| Measure | Expected reference result |
|---|---:|
| Mean error | `0.0 ms` |
| Mean absolute error | `1.2 ms` |
| Median absolute error | `1.0 ms` |
| Standard deviation | `1.414214 ms` |
| 95th-percentile absolute error | `2.0 ms` |
| Maximum absolute error | `2.0 ms` |

These values validate calculations against known synthetic inputs. They are not performance claims for a physical device or deployed system.

## What the harness checks

### Ground-truth timing

Each source timestamp is constructed from a known event time, a declared source offset, and a deterministic residual. Alignment removes only the declared offset. The harness calculates:

```text
alignment error = aligned timestamp - known ground-truth timestamp
```

It reports signed mean error, mean and median absolute error, population standard deviation, 95th-percentile absolute error, and maximum absolute error.

### Missingness

Controlled rates are applied to a 100-record fixture. Records remain present with `raw_value = null`, `missing = true`, and `missingness_status = missing`. Deterministic selection is checked by comparing affected record IDs across repeated runs.

### Provenance and export fidelity

The same provenance value must survive record construction, timestamp alignment, API-shaped dictionary conversion, JSON export, and CSV export. Canonical JSON and CSV exports are replayed 100 times and compared by SHA-256.

### Input-quality faults

The harness detects duplicate timestamps within a source, decreasing timestamp order, malformed timestamps, and values outside declared valid ranges. Sampling-rate metadata from 50 Hz, 90 Hz, and 100 Hz streams must remain unchanged.

### Event reconstruction

The canonical object-drop fixture must reconstruct offsets `-2`, `-1`, `0`, `+1`, and `+2 s`, seven metrics per offset, and all 35 `(offset, metric)` keys without omissions or unexpected records. Provenance and layer metadata must be present on every record.

## ESP32-S3 hardware-in-the-loop handoff

The next experiment should replace authored source timestamps with measurements from a versioned ESP32-S3 setup and an independent timing reference.

### Minimum setup

- ESP32-S3 firmware that records an event ID and device timestamp;
- a button or GPIO trigger;
- an LED pulse driven by the same event;
- Wi-Fi telemetry carrying the event ID and timestamp;
- an independent camera or logic analyzer observing the LED or GPIO;
- a host clock synchronization method recorded with its configuration; and
- raw firmware, network, CATEM, and reference logs retained unchanged.

### Trial procedure

1. Freeze and record CATEM commit, firmware version, board, camera or analyzer, network configuration, and clocks.
2. Trigger at least 100 uniquely identified events.
3. Capture the ESP32 timestamp, CATEM receive and aligned timestamps, and independent reference timestamp for every event.
4. Match records by event ID rather than nearest timestamp alone.
5. Report missing, duplicate, malformed, and unmatched events before exclusions.
6. Calculate signed error, mean absolute error, median absolute error, standard deviation, 95th percentile, maximum, drift over trial order, and uncertainty from the reference device.
7. Repeat under preregistered latency, jitter, and packet-loss conditions, comparing injected, independently measured, and CATEM-recorded values.

### Required result fields

At minimum, each hardware record should contain:

```text
experiment_id, trial_id, event_id, condition_id,
firmware_version, hardware_configuration_id, software_commit,
ground_truth_timestamp_utc, device_timestamp_utc,
receive_timestamp_utc, aligned_timestamp_utc,
alignment_error_ms, injected_latency_ms, measured_latency_ms,
packet_loss_condition_percent, sampling_rate_hz,
missing, missingness_status, quality_flag,
source_uri, provenance_hash, exclusion_reason
```

Acceptance thresholds must be defined before collection from the intended use and reference-device uncertainty. The synthetic `2 ms` maximum in the reference harness must not be reused as a hardware acceptance threshold.
