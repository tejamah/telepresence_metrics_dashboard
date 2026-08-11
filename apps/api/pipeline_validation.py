from __future__ import annotations

import argparse
import asyncio
import csv
import io
import json
import math
import platform
import statistics
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


API_DIR = Path(__file__).resolve().parent
ROOT = API_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import routes
from main import app


DEFAULT_OUTPUT_DIR = ROOT / "docs" / "catem"
SOURCE_CONFIG = {
    "network": {"offset_ms": 20.0, "sampling_rate_hz": 50.0},
    "tracking": {"offset_ms": 45.0, "sampling_rate_hz": 90.0},
    "sensor": {"offset_ms": 12.0, "sampling_rate_hz": 100.0},
}
EXACT_SHIFTS_MS = (10.0, 50.0, 100.0, 250.0, 500.0)
RESIDUAL_PATTERN_MS = (-2.0, -1.0, 0.0, 1.0, 2.0)


@dataclass(frozen=True)
class PipelineCheck:
    category: str
    test: str
    expected: str
    observed: str
    passed: bool


@dataclass(frozen=True)
class AsgiResponse:
    status_code: int
    headers: dict[str, str]
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body)


def _check(
    category: str,
    test: str,
    expected: Any,
    observed: Any,
    passed: bool,
) -> PipelineCheck:
    return PipelineCheck(category, test, str(expected), str(observed), bool(passed))


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


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parse_timestamp(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized).astimezone(timezone.utc)


async def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> AsgiResponse:
    body = json.dumps(payload, separators=(",", ":")).encode("utf-8") if payload is not None else b""
    request_sent = False
    messages: list[dict[str, Any]] = []

    async def receive() -> dict[str, Any]:
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {"type": "http.request", "body": body, "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    headers = [(b"host", b"validation.local")]
    if payload is not None:
        headers.extend([
            (b"content-type", b"application/json"),
            (b"content-length", str(len(body)).encode("ascii")),
        ])
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode("ascii"),
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 50000),
        "server": ("validation.local", 80),
        "root_path": "",
    }
    await app(scope, receive, send)
    start = next(message for message in messages if message["type"] == "http.response.start")
    response_body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return AsgiResponse(
        status_code=start["status"],
        headers={key.decode("latin-1"): value.decode("latin-1") for key, value in start["headers"]},
        body=response_body,
    )


def _percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    index = max(0, min(len(ordered) - 1, math.ceil(probability * len(ordered)) - 1))
    return ordered[index]


def _error_summary(errors: list[float]) -> dict[str, float | int]:
    absolute = [abs(error) for error in errors]
    return {
        "observations": len(errors),
        "mean_error_ms": round(statistics.fmean(errors), 6),
        "mean_absolute_error_ms": round(statistics.fmean(absolute), 6),
        "median_absolute_error_ms": round(statistics.median(absolute), 6),
        "standard_deviation_ms": round(statistics.pstdev(errors), 6),
        "p95_absolute_error_ms": round(_percentile(absolute, 0.95), 6),
        "maximum_absolute_error_ms": round(max(absolute), 6),
    }


def _event_payload(
    *,
    trial_id: int,
    source: str,
    truth: datetime,
    offset_ms: float,
    residual_ms: float,
    sampling_rate_hz: float,
) -> dict[str, Any]:
    source_timestamp = truth + timedelta(milliseconds=offset_ms + residual_ms)
    return {
        "session_id": trial_id,
        "participant_id": f"E2E-{trial_id:03d}",
        "source": source,
        "timestamp": _format_timestamp(source_timestamp),
        "source_clock_offset_ms": offset_ms,
        "sampling_rate_hz": sampling_rate_hz,
        "provenance": f"catem-e2e-v1:trial-{trial_id:03d}:{source}",
        "metrics": {
            "latency": float(80 + trial_id % 5),
            "agency": float(70 + trial_id % 3),
            "hrv": float(48 + trial_id % 4),
        },
    }


async def _run_pipeline(trial_count: int) -> dict[str, Any]:
    checks: list[PipelineCheck] = []
    truth = datetime(2026, 7, 1, 12, 0, 10, tzinfo=timezone.utc)

    # Exact shifts pass through FastAPI parsing, the production ingestion route,
    # synchronization, CATEM processing, and response serialization.
    routes.TELEMETRY_STREAM.clear()
    exact_errors: list[float] = []
    exact_statuses: list[int] = []
    for index, shift_ms in enumerate(EXACT_SHIFTS_MS, start=1):
        payload = _event_payload(
            trial_id=index,
            source="exact-shift",
            truth=truth,
            offset_ms=shift_ms,
            residual_ms=0.0,
            sampling_rate_hz=100.0,
        )
        response = await _request("POST", "/telemetry", payload)
        exact_statuses.append(response.status_code)
        if response.status_code == 200:
            result = response.json()
            exact_errors.append(
                round((_parse_timestamp(result["timestamp"]) - truth).total_seconds() * 1000, 6)
            )
    checks.append(_check(
        "api_ingestion",
        "Exact declared timestamp shifts through API",
        "five HTTP 200 responses with 0.0 ms errors",
        f"statuses={exact_statuses}; errors_ms={exact_errors}",
        exact_statuses == [200] * len(EXACT_SHIFTS_MS) and exact_errors == [0.0] * len(EXACT_SHIFTS_MS),
    ))

    malformed = _event_payload(
        trial_id=998,
        source="malformed",
        truth=truth,
        offset_ms=0,
        residual_ms=0,
        sampling_rate_hz=100,
    )
    malformed["timestamp"] = "not-a-timestamp"
    malformed_response = await _request("POST", "/telemetry", malformed)
    checks.append(_check(
        "api_ingestion",
        "Malformed timestamp rejected by API",
        "HTTP 422",
        f"HTTP {malformed_response.status_code}",
        malformed_response.status_code == 422,
    ))

    naive = dict(malformed)
    naive["timestamp"] = "2026-07-01T12:00:10.000"
    naive_response = await _request("POST", "/telemetry", naive)
    checks.append(_check(
        "api_ingestion",
        "Offset-free timestamp rejected by API",
        "HTTP 422",
        f"HTTP {naive_response.status_code}",
        naive_response.status_code == 422,
    ))

    routes.TELEMETRY_STREAM.clear()
    base = datetime(2026, 7, 1, 13, 0, tzinfo=timezone.utc)
    responses: list[dict[str, Any]] = []
    submitted_payloads: list[dict[str, Any]] = []
    statuses: list[int] = []
    errors: list[float] = []
    expected_errors: list[float] = []
    for trial_id in range(1, trial_count + 1):
        event_truth = base + timedelta(seconds=trial_id * 2)
        residual = RESIDUAL_PATTERN_MS[(trial_id - 1) % len(RESIDUAL_PATTERN_MS)]
        for source, config in SOURCE_CONFIG.items():
            payload = _event_payload(
                trial_id=trial_id,
                source=source,
                truth=event_truth,
                offset_ms=config["offset_ms"],
                residual_ms=residual,
                sampling_rate_hz=config["sampling_rate_hz"],
            )
            response = await _request("POST", "/telemetry", payload)
            statuses.append(response.status_code)
            if response.status_code != 200:
                continue
            result = response.json()
            submitted_payloads.append(payload)
            responses.append(result)
            errors.append(round(
                (_parse_timestamp(result["timestamp"]) - event_truth).total_seconds() * 1000,
                6,
            ))
            expected_errors.append(residual)

    expected_events = trial_count * len(SOURCE_CONFIG)
    timing = _error_summary(errors)
    expected_timing = _error_summary(expected_errors)
    checks.extend([
        _check("api_ingestion", "Repeated API ingestion status", f"{expected_events} HTTP 200 responses", f"{sum(status == 200 for status in statuses)}/{len(statuses)}", statuses == [200] * expected_events),
        _check("api_ingestion", "Telemetry stream persistence", expected_events, len(routes.TELEMETRY_STREAM), len(routes.TELEMETRY_STREAM) == expected_events),
        _check("synchronization", "Aligned timing observations", expected_events, timing["observations"], timing["observations"] == expected_events),
        _check("synchronization", "Signed alignment errors", "match authored residuals", f"matched={errors == expected_errors}", errors == expected_errors),
        _check("synchronization", "Mean alignment error", f"{expected_timing['mean_error_ms']} ms", f"{timing['mean_error_ms']} ms", timing["mean_error_ms"] == expected_timing["mean_error_ms"]),
        _check("synchronization", "Mean absolute alignment error", f"{expected_timing['mean_absolute_error_ms']} ms", f"{timing['mean_absolute_error_ms']} ms", timing["mean_absolute_error_ms"] == expected_timing["mean_absolute_error_ms"]),
        _check("synchronization", "Median absolute alignment error", f"{expected_timing['median_absolute_error_ms']} ms", f"{timing['median_absolute_error_ms']} ms", timing["median_absolute_error_ms"] == expected_timing["median_absolute_error_ms"]),
        _check("synchronization", "P95 absolute alignment error", f"{expected_timing['p95_absolute_error_ms']} ms", f"{timing['p95_absolute_error_ms']} ms", timing["p95_absolute_error_ms"] == expected_timing["p95_absolute_error_ms"]),
        _check("synchronization", "Maximum absolute alignment error", f"{expected_timing['maximum_absolute_error_ms']} ms", f"{timing['maximum_absolute_error_ms']} ms", timing["maximum_absolute_error_ms"] == expected_timing["maximum_absolute_error_ms"]),
    ])

    record_count = sum(len(response["measurement_records"]) for response in responses)
    input_source_timestamps_preserved = all(
        response["source_timestamp"] == submitted["timestamp"]
        for submitted, response in zip(submitted_payloads, responses)
    )
    input_provenance_preserved = all(
        response["provenance"] == submitted["provenance"]
        for submitted, response in zip(submitted_payloads, responses)
    )
    input_sampling_rates_preserved = all(
        response["sampling_rate_hz"] == submitted["sampling_rate_hz"]
        for submitted, response in zip(submitted_payloads, responses)
    )
    input_metrics_preserved = all(
        response["metrics"] == submitted["metrics"]
        for submitted, response in zip(submitted_payloads, responses)
    )
    source_timestamps_preserved = all(
        record["source_timestamp"] == response["source_timestamp"]
        for response in responses
        for record in response["measurement_records"]
    )
    aligned_timestamps_preserved = all(
        record["timestamp"] == response["timestamp"]
        for response in responses
        for record in response["measurement_records"]
    )
    provenance_preserved = all(
        record["provenance"] == response["provenance"]
        for response in responses
        for record in response["measurement_records"]
    )
    sampling_rates_preserved = all(
        record["sampling_rate_hz"] == response["sampling_rate_hz"]
        for response in responses
        for record in response["measurement_records"]
    )
    raw_values_preserved = all(
        next(record for record in response["measurement_records"] if record["metric"] == "latency")["raw_value"]
        == response["metrics"]["latency"]
        for response in responses
    )
    missingness_explicit = all(
        any(record["missing"] and record["missingness_status"] == "missing" for record in response["measurement_records"])
        for response in responses
    )
    catem_complete = all(
        response["catem"].get("framework_version") == routes.CATEM_VERSION
        and response["catem"].get("layers")
        and response["catem"].get("evidence_profile")
        for response in responses
    )
    checks.extend([
        _check("measurement_contract", "Ingested source timestamps preserved", "all submitted events", f"events={len(responses)}; complete={input_source_timestamps_preserved}", input_source_timestamps_preserved),
        _check("measurement_contract", "Ingested provenance preserved", "all submitted events", f"events={len(responses)}; complete={input_provenance_preserved}", input_provenance_preserved),
        _check("measurement_contract", "Ingested sampling rates preserved", "all submitted events", f"events={len(responses)}; complete={input_sampling_rates_preserved}", input_sampling_rates_preserved),
        _check("measurement_contract", "Ingested metric dictionaries preserved", "all submitted events", f"events={len(responses)}; complete={input_metrics_preserved}", input_metrics_preserved),
        _check("measurement_contract", "Source timestamps propagated", "all measurement records", f"records={record_count}; complete={source_timestamps_preserved}", source_timestamps_preserved),
        _check("measurement_contract", "Aligned timestamps propagated", "all measurement records", f"records={record_count}; complete={aligned_timestamps_preserved}", aligned_timestamps_preserved),
        _check("measurement_contract", "Provenance propagated unchanged", "all measurement records", f"records={record_count}; complete={provenance_preserved}", provenance_preserved),
        _check("measurement_contract", "Sampling rates propagated unchanged", "all measurement records", f"records={record_count}; complete={sampling_rates_preserved}", sampling_rates_preserved),
        _check("measurement_contract", "Raw latency values preserved", "all events", f"events={len(responses)}; complete={raw_values_preserved}", raw_values_preserved),
        _check("measurement_contract", "Expected missing metrics explicit", "at least one explicit missing record per event", f"events={len(responses)}; complete={missingness_explicit}", missingness_explicit),
        _check("catem_processing", "CATEM assessment included", "versioned layers and evidence profile for every event", f"events={len(responses)}; complete={catem_complete}", catem_complete),
    ])

    json_export_a = await _request("GET", "/telemetry/export/json")
    json_export_b = await _request("GET", "/telemetry/export/json")
    csv_export_a = await _request("GET", "/telemetry/export/csv")
    csv_export_b = await _request("GET", "/telemetry/export/csv")
    json_payload = json_export_a.json() if json_export_a.status_code == 200 else {"events": []}
    json_events = json_payload.get("events", [])
    csv_rows = list(csv.DictReader(io.StringIO(csv_export_a.body.decode("utf-8")))) if csv_export_a.status_code == 200 else []
    json_provenance = all(
        record["provenance"] == event["provenance"]
        for event in json_events
        for record in event["measurement_records"]
    )
    csv_provenance = all(row["provenance"].startswith("catem-e2e-v1:") for row in csv_rows)
    csv_timestamps = all(row["source_timestamp"] and row["aligned_timestamp"] for row in csv_rows)
    checks.extend([
        _check("api_export", "JSON export endpoint", "HTTP 200", f"HTTP {json_export_a.status_code}", json_export_a.status_code == 200),
        _check("api_export", "JSON event completeness", expected_events, len(json_events), len(json_events) == expected_events),
        _check("api_export", "JSON event fidelity", "exported events equal API responses", f"complete={json_events == responses}", json_events == responses),
        _check("api_export", "JSON provenance integrity", "all measurement records", f"complete={json_provenance}", json_provenance),
        _check("api_export", "Deterministic JSON export", "identical bytes on replay", f"identical={json_export_a.body == json_export_b.body}", json_export_a.body == json_export_b.body),
        _check("api_export", "CSV export endpoint", "HTTP 200", f"HTTP {csv_export_a.status_code}", csv_export_a.status_code == 200),
        _check("api_export", "CSV measurement-record completeness", record_count, len(csv_rows), len(csv_rows) == record_count),
        _check("api_export", "CSV provenance integrity", "all measurement records", f"complete={csv_provenance}", csv_provenance),
        _check("api_export", "CSV timestamp completeness", "source and aligned timestamps on every row", f"complete={csv_timestamps}", csv_timestamps),
        _check("api_export", "Deterministic CSV export", "identical bytes on replay", f"identical={csv_export_a.body == csv_export_b.body}", csv_export_a.body == csv_export_b.body),
    ])

    routes.TELEMETRY_STREAM.clear()
    passed = sum(check.passed for check in checks)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "milestone": "CATEM End-to-End Pipeline Validation v1",
        "scope": (
            "In-process ASGI validation of FastAPI request parsing, telemetry ingestion, declared-offset "
            "synchronization, CATEM processing, measurement-contract generation, and JSON/CSV export."
        ),
        "interpretation_boundary": (
            "The harness supplies known synthetic timestamps and declared clock offsets. It validates the "
            "CATEM software path, not clock-offset estimation, HTTP socket transport, hardware timing "
            "accuracy, construct validity, causal validity, or human-subject effectiveness."
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
            "transport": "in-process ASGI 3.0",
        },
        "configuration": {
            "trial_count": trial_count,
            "source_count": len(SOURCE_CONFIG),
            "expected_events": expected_events,
            "exact_shifts_ms": list(EXACT_SHIFTS_MS),
            "source_configuration": SOURCE_CONFIG,
            "residual_pattern_ms": list(RESIDUAL_PATTERN_MS),
        },
        "quantitative_results": {
            "timing": timing,
            "api_events": len(responses),
            "measurement_records": record_count,
            "json_export_events": len(json_events),
            "csv_export_records": len(csv_rows),
        },
        "summary": {
            "checks": len(checks),
            "passed": passed,
            "failed": len(checks) - passed,
        },
        "checks": [asdict(check) for check in checks],
    }


def run_pipeline_validation(*, trial_count: int = 100) -> dict[str, Any]:
    if trial_count < 100:
        raise ValueError("trial_count must be at least 100")
    return asyncio.run(_run_pipeline(trial_count))


def write_outputs(payload: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "pipeline_validation_results.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "pipeline_validation_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["category", "test", "expected", "observed", "passed"],
        )
        writer.writeheader()
        writer.writerows(payload["checks"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run CATEM end-to-end ingestion, processing, contract, and export validation."
    )
    parser.add_argument("--trials", type=int, default=100)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    payload = run_pipeline_validation(trial_count=args.trials)
    write_outputs(payload, args.output_dir)
    print(json.dumps(payload["summary"], sort_keys=True))
    print(json.dumps(payload["quantitative_results"], sort_keys=True))
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
