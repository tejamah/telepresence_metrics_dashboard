from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import platform
import statistics
import subprocess
import sys
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable


API_DIR = Path(__file__).resolve().parent
ROOT = API_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import routes


DEFAULT_OUTPUT_DIR = ROOT / "docs" / "catem"
TIMESTAMP_SHIFTS_MS = (10.0, 50.0, 100.0, 250.0, 500.0)
MISSINGNESS_RATES = (0, 5, 10, 25, 50)
SOURCE_CONFIG = {
    "network": {"offset_ms": 20.0, "sampling_rate_hz": 50.0},
    "tracking": {"offset_ms": 45.0, "sampling_rate_hz": 90.0},
    "sensor": {"offset_ms": 12.0, "sampling_rate_hz": 100.0},
}
RESIDUAL_PATTERN_MS = (-2.0, -1.0, 0.0, 1.0, 2.0)


@dataclass(frozen=True)
class ValidationCheck:
    category: str
    test: str
    expected: str
    observed: str
    passed: bool


@dataclass(frozen=True)
class GroundTruthRecord:
    record_id: str
    trial_id: int
    source: str
    metric: str
    raw_value: float | None
    unit: str
    source_timestamp: str
    receive_timestamp: str
    ground_truth_timestamp: str
    injected_offset_ms: float
    sampling_rate_hz: float
    valid_range: tuple[float, float]
    missing: bool
    missingness_status: str
    preprocessing: str
    provenance: str
    transform_version: str
    interpretation_boundary: str
    aligned_timestamp: str | None = None
    alignment_error_ms: float | None = None


def _check(
    category: str,
    test: str,
    expected: Any,
    observed: Any,
    passed: bool,
) -> ValidationCheck:
    return ValidationCheck(category, test, str(expected), str(observed), bool(passed))


def _git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        return "unavailable"


def _parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        raise ValueError("timestamp must include a UTC offset")
    return parsed.astimezone(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _record_dict(record: GroundTruthRecord) -> dict[str, Any]:
    payload = asdict(record)
    payload["valid_range"] = list(record.valid_range)
    return payload


def _canonical_csv(records: Iterable[GroundTruthRecord]) -> bytes:
    rows = [_record_dict(record) for record in records]
    if not rows:
        return b""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    for row in rows:
        row["valid_range"] = json.dumps(row["valid_range"], separators=(",", ":"))
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


def make_record(
    *,
    trial_id: int,
    source: str,
    ground_truth: datetime,
    injected_offset_ms: float,
    residual_ms: float = 0.0,
    sampling_rate_hz: float = 100.0,
) -> GroundTruthRecord:
    source_time = ground_truth + timedelta(milliseconds=injected_offset_ms + residual_ms)
    receive_time = source_time + timedelta(milliseconds=3)
    return GroundTruthRecord(
        record_id=f"trial-{trial_id:03d}:{source}",
        trial_id=trial_id,
        source=source,
        metric="event_marker",
        raw_value=1.0,
        unit="binary",
        source_timestamp=_format_timestamp(source_time),
        receive_timestamp=_format_timestamp(receive_time),
        ground_truth_timestamp=_format_timestamp(ground_truth),
        injected_offset_ms=injected_offset_ms,
        sampling_rate_hz=sampling_rate_hz,
        valid_range=(0.0, 1.0),
        missing=False,
        missingness_status="observed",
        preprocessing="none_declared",
        provenance=f"synthetic-ground-truth-v1:trial-{trial_id:03d}:{source}",
        transform_version="catem-validation-v1",
        interpretation_boundary=(
            "Deterministic synthetic timing fixture; not a hardware measurement, "
            "participant observation, or construct-validity result."
        ),
    )


def align_record(record: GroundTruthRecord) -> GroundTruthRecord:
    source_time = _parse_timestamp(record.source_timestamp)
    aligned = source_time - timedelta(milliseconds=record.injected_offset_ms)
    truth = _parse_timestamp(record.ground_truth_timestamp)
    error_ms = (aligned - truth).total_seconds() * 1000
    return replace(
        record,
        aligned_timestamp=_format_timestamp(aligned),
        alignment_error_ms=round(error_ms, 6),
    )


def validate_records(records: list[GroundTruthRecord]) -> dict[str, list[str]]:
    issues: dict[str, list[str]] = {
        "duplicate_timestamp": [],
        "unordered_timestamp": [],
        "malformed_timestamp": [],
        "out_of_range": [],
    }
    seen: set[tuple[str, str]] = set()
    previous_by_source: dict[str, datetime] = {}
    for record in records:
        key = (record.source, record.source_timestamp)
        if key in seen:
            issues["duplicate_timestamp"].append(record.record_id)
        seen.add(key)
        try:
            timestamp = _parse_timestamp(record.source_timestamp)
        except (TypeError, ValueError):
            issues["malformed_timestamp"].append(record.record_id)
            continue
        previous = previous_by_source.get(record.source)
        if previous is not None and timestamp < previous:
            issues["unordered_timestamp"].append(record.record_id)
        previous_by_source[record.source] = timestamp
        if record.raw_value is not None:
            low, high = record.valid_range
            if record.raw_value < low or record.raw_value > high:
                issues["out_of_range"].append(record.record_id)
    return issues


def apply_missingness(records: list[GroundTruthRecord], rate_percent: int) -> list[GroundTruthRecord]:
    if not 0 <= rate_percent <= 100:
        raise ValueError("missingness rate must be between 0 and 100")
    missing_count = round(len(records) * rate_percent / 100)
    missing_indices = set(range(missing_count))
    return [
        replace(
            record,
            raw_value=None if index in missing_indices else record.raw_value,
            missing=index in missing_indices,
            missingness_status="missing" if index in missing_indices else "observed",
        )
        for index, record in enumerate(records)
    ]


def _percentile(values: list[float], probability: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(probability * len(ordered)) - 1))
    return ordered[index]


def _timing_summary(records: list[GroundTruthRecord]) -> dict[str, float | int]:
    errors = [float(record.alignment_error_ms) for record in records if record.alignment_error_ms is not None]
    return _error_summary(errors)


def _error_summary(errors: list[float]) -> dict[str, float | int]:
    absolute_errors = [abs(value) for value in errors]
    return {
        "observations": len(errors),
        "mean_error_ms": round(statistics.fmean(errors), 6),
        "mean_absolute_error_ms": round(statistics.fmean(absolute_errors), 6),
        "median_absolute_error_ms": round(statistics.median(absolute_errors), 6),
        "standard_deviation_ms": round(statistics.pstdev(errors), 6),
        "p95_absolute_error_ms": round(_percentile(absolute_errors, 0.95), 6),
        "maximum_absolute_error_ms": round(max(absolute_errors), 6),
    }


def _build_trials(trial_count: int) -> list[GroundTruthRecord]:
    base = datetime(2026, 7, 1, 12, 0, tzinfo=timezone.utc)
    records: list[GroundTruthRecord] = []
    for trial_id in range(1, trial_count + 1):
        truth = base + timedelta(seconds=trial_id * 2)
        residual = RESIDUAL_PATTERN_MS[(trial_id - 1) % len(RESIDUAL_PATTERN_MS)]
        for source, config in SOURCE_CONFIG.items():
            records.append(make_record(
                trial_id=trial_id,
                source=source,
                ground_truth=truth,
                injected_offset_ms=config["offset_ms"],
                residual_ms=residual,
                sampling_rate_hz=config["sampling_rate_hz"],
            ))
    return records


def run_validation(*, replay_count: int = 100, trial_count: int = 100) -> dict[str, Any]:
    if replay_count < 100:
        raise ValueError("replay_count must be at least 100")
    if trial_count < 100:
        raise ValueError("trial_count must be at least 100")

    checks: list[ValidationCheck] = []
    truth = datetime(2026, 7, 1, 12, 0, 10, tzinfo=timezone.utc)

    # Exact timestamp-offset recovery.
    for shift_ms in TIMESTAMP_SHIFTS_MS:
        aligned = align_record(make_record(
            trial_id=1,
            source="timestamp-shift",
            ground_truth=truth,
            injected_offset_ms=shift_ms,
        ))
        checks.append(_check(
            "ground_truth_timing",
            f"Exact +{int(shift_ms)} ms timestamp shift",
            "0.0 ms alignment error",
            f"{aligned.alignment_error_ms} ms",
            aligned.alignment_error_ms == 0.0,
        ))

    trials = _build_trials(trial_count)
    aligned_trials = [align_record(record) for record in trials]
    timing = _timing_summary(aligned_trials)
    expected_errors = [
        RESIDUAL_PATTERN_MS[(trial_id - 1) % len(RESIDUAL_PATTERN_MS)]
        for trial_id in range(1, trial_count + 1)
        for _ in SOURCE_CONFIG
    ]
    expected_timing = _error_summary(expected_errors)
    expected_observations = trial_count * len(SOURCE_CONFIG)
    checks.extend([
        _check("ground_truth_timing", "Repeated trial observation count", expected_observations, timing["observations"], timing["observations"] == expected_observations),
        _check("ground_truth_timing", "Mean alignment error", f"{expected_timing['mean_error_ms']} ms", f"{timing['mean_error_ms']} ms", timing["mean_error_ms"] == expected_timing["mean_error_ms"]),
        _check("ground_truth_timing", "Mean absolute alignment error", f"{expected_timing['mean_absolute_error_ms']} ms", f"{timing['mean_absolute_error_ms']} ms", timing["mean_absolute_error_ms"] == expected_timing["mean_absolute_error_ms"]),
        _check("ground_truth_timing", "Median absolute alignment error", f"{expected_timing['median_absolute_error_ms']} ms", f"{timing['median_absolute_error_ms']} ms", timing["median_absolute_error_ms"] == expected_timing["median_absolute_error_ms"]),
        _check("ground_truth_timing", "95th-percentile absolute alignment error", f"{expected_timing['p95_absolute_error_ms']} ms", f"{timing['p95_absolute_error_ms']} ms", timing["p95_absolute_error_ms"] == expected_timing["p95_absolute_error_ms"]),
        _check("ground_truth_timing", "Maximum absolute alignment error", f"{expected_timing['maximum_absolute_error_ms']} ms", f"{timing['maximum_absolute_error_ms']} ms", timing["maximum_absolute_error_ms"] == expected_timing["maximum_absolute_error_ms"]),
    ])

    # Controlled missingness retains explicit records rather than deleting them.
    missingness_fixture = _build_trials(100)[:100]
    for rate in MISSINGNESS_RATES:
        incomplete = apply_missingness(missingness_fixture, rate)
        missing = [record for record in incomplete if record.missing]
        reported_rate = len(missing) / len(incomplete) * 100
        flags_consistent = all(
            (record.raw_value is None) == record.missing
            and record.missingness_status == ("missing" if record.missing else "observed")
            for record in incomplete
        )
        checks.append(_check(
            "missingness",
            f"Controlled {rate}% missingness",
            f"{rate:.1f}% reported with consistent flags",
            f"{reported_rate:.1f}% reported; flags_consistent={flags_consistent}",
            reported_rate == float(rate) and flags_consistent,
        ))
    removal_a = apply_missingness(missingness_fixture, 25)
    removal_b = apply_missingness(missingness_fixture, 25)
    missing_ids_a = [record.record_id for record in removal_a if record.missing]
    missing_ids_b = [record.record_id for record in removal_b if record.missing]
    checks.append(_check(
        "missingness",
        "Deterministic missingness selection",
        "identical missing record IDs",
        f"{len(missing_ids_a)} IDs; identical={missing_ids_a == missing_ids_b}",
        missing_ids_a == missing_ids_b,
    ))

    # Provenance must survive alignment and both export formats unchanged.
    source_provenance = [record.provenance for record in trials]
    aligned_provenance = [record.provenance for record in aligned_trials]
    api_rows = [_record_dict(record) for record in aligned_trials]
    api_provenance = [row["provenance"] for row in api_rows]
    json_rows = json.loads(_canonical_json(api_rows))
    json_provenance = [row["provenance"] for row in json_rows]
    csv_rows = list(csv.DictReader(io.StringIO(_canonical_csv(aligned_trials).decode("utf-8"))))
    csv_provenance = [row["provenance"] for row in csv_rows]
    checks.extend([
        _check("provenance", "Ingestion to alignment", "provenance unchanged", f"{len(aligned_provenance)} records", source_provenance == aligned_provenance),
        _check("provenance", "Alignment to API object", "provenance unchanged", f"{len(api_provenance)} records", source_provenance == api_provenance),
        _check("provenance", "API object to JSON export", "provenance unchanged", f"{len(json_provenance)} records", source_provenance == json_provenance),
        _check("provenance", "API object to CSV export", "provenance unchanged", f"{len(csv_provenance)} records", source_provenance == csv_provenance),
        _check("provenance", "Unique source lineage", f"{len(trials)} unique provenance values", len(set(source_provenance)), len(set(source_provenance)) == len(trials)),
    ])

    # Deterministic replay and export hashing.
    json_hashes = [_sha256(_canonical_json(api_rows)) for _ in range(replay_count)]
    csv_hashes = [_sha256(_canonical_csv(aligned_trials)) for _ in range(replay_count)]
    checks.extend([
        _check("reproducibility", f"JSON replay ({replay_count} runs)", "one unique SHA-256", len(set(json_hashes)), len(set(json_hashes)) == 1),
        _check("reproducibility", f"CSV replay ({replay_count} runs)", "one unique SHA-256", len(set(csv_hashes)), len(set(csv_hashes)) == 1),
        _check("reproducibility", "Stable JSON row count", len(aligned_trials), len(json_rows), len(json_rows) == len(aligned_trials)),
        _check("reproducibility", "Stable CSV row count", len(aligned_trials), len(csv_rows), len(csv_rows) == len(aligned_trials)),
    ])

    # Input-quality faults are detected and reported without silent correction.
    base_record = make_record(
        trial_id=901,
        source="quality-test",
        ground_truth=truth,
        injected_offset_ms=10,
    )
    duplicate = replace(base_record, record_id="duplicate")
    later = replace(
        base_record,
        record_id="later",
        source_timestamp=_format_timestamp(_parse_timestamp(base_record.source_timestamp) + timedelta(seconds=1)),
    )
    earlier = replace(
        base_record,
        record_id="earlier",
        source_timestamp=_format_timestamp(_parse_timestamp(base_record.source_timestamp) - timedelta(seconds=1)),
    )
    malformed = replace(base_record, record_id="malformed", source_timestamp="2026-99-not-a-time")
    out_of_range = replace(base_record, record_id="out-of-range", raw_value=2.0)
    quality_cases = {
        "duplicate_timestamp": validate_records([base_record, duplicate]),
        "unordered_timestamp": validate_records([later, earlier]),
        "malformed_timestamp": validate_records([malformed]),
        "out_of_range": validate_records([out_of_range]),
    }
    for issue_name, result in quality_cases.items():
        checks.append(_check(
            "input_quality",
            issue_name.replace("_", " ").title(),
            "one flagged record",
            result[issue_name],
            len(result[issue_name]) == 1,
        ))
    clean_issues = validate_records([base_record, later])
    checks.append(_check(
        "input_quality",
        "Clean ordered stream",
        "no issues",
        clean_issues,
        not any(clean_issues.values()),
    ))

    mixed_rates = {record.source: record.sampling_rate_hz for record in trials[:3]}
    checks.append(_check(
        "input_quality",
        "Mixed sampling rates preserved",
        {name: config["sampling_rate_hz"] for name, config in SOURCE_CONFIG.items()},
        mixed_rates,
        mixed_rates == {name: config["sampling_rate_hz"] for name, config in SOURCE_CONFIG.items()},
    ))

    # Event reconstruction reuses the canonical 5 x 7 CATEM fixture.
    event_window = routes.object_drop_event_window()
    offsets = [sample["offset_seconds"] for sample in event_window["samples"]]
    event_zero = next(sample for sample in event_window["samples"] if sample["offset_seconds"] == 0)
    records = event_window["records"]
    expected_metrics = {
        "latency": 220.0,
        "packet_loss": 12.0,
        "tracking_dropout": 15.0,
        "workload": 82.0,
        "heart_rate": 112.0,
        "agency": 58.0,
        "task_error": 1.0,
    }
    event_keys = {(record["offset_seconds"], record["metric"]) for record in records}
    expected_keys = {(offset, metric) for offset in offsets for metric in expected_metrics}
    checks.extend([
        _check("event_reconstruction", "Canonical offsets", [-2, -1, 0, 1, 2], offsets, offsets == [-2, -1, 0, 1, 2]),
        _check("event_reconstruction", "Canonical record count", 35, len(records), len(records) == 35),
        _check("event_reconstruction", "Event-zero values", expected_metrics, event_zero["metrics"], event_zero["metrics"] == expected_metrics),
        _check("event_reconstruction", "Window key recall", "35/35", f"{len(event_keys & expected_keys)}/35", event_keys == expected_keys),
        _check("event_reconstruction", "Window key precision", "no unexpected keys", len(event_keys - expected_keys), not event_keys - expected_keys),
        _check("event_reconstruction", "Record provenance completeness", "35/35", sum(bool(record.get("provenance")) for record in records), all(record.get("provenance") for record in records)),
        _check("event_reconstruction", "Record layer completeness", "35/35", sum(bool(record.get("layer")) for record in records), all(record.get("layer") for record in records)),
    ])

    passed = sum(check.passed for check in checks)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "milestone": "CATEM Validation v1: synthetic ground-truth measurement validation",
        "scope": (
            "Deterministic synthetic validation of timestamp alignment, provenance, missingness, "
            "input-quality detection, reproducible export, and event reconstruction."
        ),
        "interpretation_boundary": (
            "These results do not establish hardware synchronization accuracy, construct or ecological "
            "validity, causal validity, predictive accuracy, human-subject effectiveness, or production readiness."
        ),
        "software": {
            "software_version": routes.SOFTWARE_VERSION,
            "catem_version": routes.CATEM_VERSION,
            "api_schema_version": routes.API_SCHEMA_VERSION,
            "repository_commit": _git_commit(),
        },
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "operating_system": platform.platform(),
            "harness": "Python standard-library CATEM Validation v1 harness",
        },
        "configuration": {
            "replay_count": replay_count,
            "trial_count": trial_count,
            "source_count": len(SOURCE_CONFIG),
            "timestamp_shifts_ms": list(TIMESTAMP_SHIFTS_MS),
            "missingness_rates_percent": list(MISSINGNESS_RATES),
            "source_configuration": SOURCE_CONFIG,
            "residual_pattern_ms": list(RESIDUAL_PATTERN_MS),
        },
        "quantitative_results": {
            "timing": timing,
            "json_sha256": json_hashes[0],
            "csv_sha256": csv_hashes[0],
            "event_reconstruction": {
                "expected_records": len(expected_keys),
                "recovered_records": len(event_keys & expected_keys),
                "unexpected_records": len(event_keys - expected_keys),
                "recall": round(len(event_keys & expected_keys) / len(expected_keys), 6),
                "precision": round(len(event_keys & expected_keys) / len(event_keys), 6),
            },
        },
        "summary": {
            "checks": len(checks),
            "passed": passed,
            "failed": len(checks) - passed,
        },
        "checks": [asdict(check) for check in checks],
    }


def write_outputs(payload: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "validation_v1_results.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "validation_v1_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["category", "test", "expected", "observed", "passed"],
        )
        writer.writeheader()
        writer.writerows(payload["checks"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run CATEM Validation v1 synthetic ground-truth checks."
    )
    parser.add_argument("--replays", type=int, default=100)
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    payload = run_validation(replay_count=args.replays, trial_count=args.trials)
    write_outputs(payload, args.output_dir)
    print(json.dumps(payload["summary"], sort_keys=True))
    print(json.dumps(payload["quantitative_results"]["timing"], sort_keys=True))
    print(f"json_sha256={payload['quantitative_results']['json_sha256']}")
    print(f"csv_sha256={payload['quantitative_results']['csv_sha256']}")
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
