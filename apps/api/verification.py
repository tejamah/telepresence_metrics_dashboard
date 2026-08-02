from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import io
import json
import platform
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile, WebSocketDisconnect


API_DIR = Path(__file__).resolve().parent
RUNTIME_ROOT = next(
    candidate
    for candidate in (API_DIR.parents[1], API_DIR.parent)
    if (candidate / "services").exists()
)
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

import routes


ROOT = API_DIR.parents[1]
DEFAULT_OUTPUT_DIR = (
    ROOT / "catem_latex_paper" / "verification"
    if (ROOT / "catem_latex_paper").exists()
    else ROOT / "reproducibility" / "verification"
)


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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


@dataclass
class VerificationResult:
    category: str
    test: str
    expected: str
    observed: str
    passed: bool


def _result(category: str, test: str, expected: Any, observed: Any, passed: bool) -> VerificationResult:
    return VerificationResult(category, test, str(expected), str(observed), bool(passed))


class _OneFrameWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.payload: dict[str, Any] | None = None

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, payload: dict[str, Any]) -> None:
        self.payload = payload
        raise WebSocketDisconnect()


def run_verification() -> dict[str, Any]:
    results: list[VerificationResult] = []
    routes.SESSIONS.clear()
    routes.TELEMETRY_STREAM.clear()
    routes._seed()
    fixture_a = routes.SESSIONS[0]
    fixture_b = routes.SESSIONS[1]
    base = dict(fixture_b.metrics)

    # Functional verification: CSV validation and ingestion.
    invalid_upload = UploadFile(filename="fixture.txt", file=io.BytesIO(b"not,csv\n"))
    invalid_status = None
    try:
        asyncio.run(routes.upload_csv(invalid_upload))
    except HTTPException as exc:
        invalid_status = exc.status_code
    results.append(_result("functional", "Invalid CSV extension", "HTTP 400", f"HTTP {invalid_status}", invalid_status == 400))

    csv_payload = (
        "participant_id,task_type,setup,session_time,latency,agency,hrv\n"
        "Fixture-C,Verification task,Test adapter,2026-07-01T14:32:18,118,72,48\n"
    ).encode("utf-8")
    valid_upload = UploadFile(filename="fixture.csv", file=io.BytesIO(csv_payload))
    valid_response = asyncio.run(routes.upload_csv(valid_upload))
    results.append(_result("functional", "Valid CSV ingestion", "1 row created", f"{valid_response['count']} row created", valid_response["count"] == 1))

    session_response = routes._session_response(fixture_b)
    serialized = json.dumps(session_response, sort_keys=True)
    required_session_objects = {
        "software_version",
        "api_schema_version",
        "metrics",
        "catem",
        "measurement_records",
    }
    required_catem_objects = {
        "framework_version",
        "layers",
        "evidence_profile",
        "propositions",
    }
    proposition_fields = {"id", "name", "status", "evidence"}
    catem = session_response.get("catem", {})
    propositions = catem.get("propositions", []) if isinstance(catem, dict) else []
    api_schema_valid = bool(
        serialized
        and required_session_objects <= set(session_response)
        and required_catem_objects <= set(catem)
        and isinstance(catem.get("evidence_profile"), dict)
        and isinstance(catem.get("layers"), dict)
        and propositions
        and all(proposition_fields <= set(item) for item in propositions)
        and isinstance(session_response.get("measurement_records"), list)
    )
    results.append(_result(
        "functional",
        "API schema validation",
        "required response objects present and schema-valid",
        "session, CATEM, evidence-condition, proposition-trace, and measurement-record objects present",
        api_schema_valid,
    ))

    event_window = routes.object_drop_event_window()
    event_offsets = [sample["offset_seconds"] for sample in event_window["samples"]]
    event_sample = next(sample for sample in event_window["samples"] if sample["offset_seconds"] == 0)
    event_records = event_window["records"]
    event_window_ok = bool(
        event_offsets == [-2, -1, 0, 1, 2]
        and event_sample["metrics"] == {
            "latency": 220.0,
            "packet_loss": 12.0,
            "tracking_dropout": 15.0,
            "workload": 82.0,
            "heart_rate": 112.0,
            "agency": 58.0,
            "task_error": 1.0,
        }
        and len(event_records) == 35
        and all(record.get("source") and record.get("layer") for record in event_records)
    )
    results.append(_result(
        "functional",
        "Canonical event-window export",
        "five aligned samples with traceable t=0 values",
        f"{len(event_window['samples'])} samples; {len(event_records)} records; offsets={event_offsets}",
        event_window_ok,
    ))

    records = session_response["measurement_records"]
    required_record_fields = {
        "metric", "construct", "layer", "raw_value", "unit", "direction",
        "instrument_or_sensor", "timestamp", "sampling_rate_hz", "valid_range",
        "missing", "missingness_status", "preprocessing", "source", "provenance",
        "transform_version", "interpretation_boundary",
    }
    contract_complete = bool(records) and all(required_record_fields <= set(record) for record in records)
    results.append(_result("functional", "Measurement-contract export", "all required fields present", f"{len(records)} records", contract_complete))

    socket = _OneFrameWebSocket()
    asyncio.run(routes.telemetry_socket(socket))
    websocket_ok = bool(
        socket.accepted
        and socket.payload
        and socket.payload.get("catem")
        and socket.payload.get("measurement_records")
    )
    results.append(_result("functional", "WebSocket frame generation", "one complete frame", "complete" if websocket_ok else "incomplete", websocket_ok))

    # Deterministic reproducibility.
    fixture_hash = _canonical_hash(base)
    replay_outputs = [routes.catem_assessment(dict(base)) for _ in range(3)]
    replay_hashes = [_canonical_hash(item) for item in replay_outputs]
    replay_passed = len(set(replay_hashes)) == 1
    results.append(_result("reproducibility", "Identical fixture replay", "identical output hashes", ",".join(replay_hashes), replay_passed))

    # Controlled fault injection.
    baseline = routes.catem_assessment(base)
    baseline_human_coverage = baseline["layers"]["human_state"]["coverage"]
    missing_hrv = dict(base)
    missing_hrv.pop("hrv")
    missing_hrv_result = routes.catem_assessment(missing_hrv)
    hrv_coverage = missing_hrv_result["layers"]["human_state"]["coverage"]
    hrv_listed = "hrv" in missing_hrv_result["layers"]["human_state"]["missing_metrics"]
    results.append(_result(
        "fault_injection",
        "Missing HRV field",
        "coverage decreases and HRV is listed",
        f"{baseline_human_coverage}->{hrv_coverage}; listed={hrv_listed}",
        hrv_coverage < baseline_human_coverage and hrv_listed,
    ))

    missing_physiology = dict(base)
    missing_physiology.pop("heart_rate")
    missing_physiology.pop("hrv")
    physiology_result = routes.catem_assessment(missing_physiology)
    physiology_coverage = physiology_result["layers"]["human_state"]["coverage"]
    results.append(_result(
        "fault_injection",
        "Missing physiological records",
        "human-state coverage decreases",
        f"{baseline_human_coverage}->{physiology_coverage}",
        physiology_coverage < baseline_human_coverage,
    ))

    baseline_system = baseline["layers"]["system"]["score"]
    for name, injected in (("latency", 220), ("jitter", 70), ("packet_loss", 12), ("tracking_dropout", 15)):
        fault = dict(base)
        fault[name] = injected
        observed_system = routes.catem_assessment(fault)["layers"]["system"]["score"]
        results.append(_result(
            "fault_injection",
            f"Increased {name}",
            "system-layer score decreases",
            f"{baseline_system}->{observed_system}",
            observed_system < baseline_system,
        ))

    baseline_sync = baseline["evidence_profile"]["synchronization_quality"]
    timestamp_fault = dict(base)
    timestamp_fault["timestamp_accuracy"] = 30
    fault_sync = routes.catem_assessment(timestamp_fault)["evidence_profile"]["synchronization_quality"]
    results.append(_result(
        "fault_injection",
        "Timestamp offset",
        "synchronization quality decreases",
        f"{baseline_sync}->{fault_sync}",
        fault_sync < baseline_sync,
    ))

    governance_fault = dict(base)
    governance_fault["adaptation_disclosed"] = 0
    governance_fault["override_available"] = 1
    p6 = next(item for item in routes.catem_assessment(governance_fault)["propositions"] if item["id"] == "P6")
    results.append(_result("fault_injection", "Adaptation without disclosure", "P6 at_risk", f"P6 {p6['status']}", p6["status"] == "at_risk"))

    numeric_value = routes._numeric("not-a-number")
    results.append(_result("fault_injection", "Invalid numeric input", "flagged as nonnumeric", repr(numeric_value), numeric_value is None))

    baseline_metrics, baseline_state = routes.SIMULATOR.simulate(base, 0)
    degraded_metrics, degraded_state = routes.SIMULATOR.simulate(base, 22)
    simulator_passed = all(
        degraded_metrics[name] > baseline_metrics[name]
        for name in ("latency", "jitter", "packet_loss")
    ) and baseline_state["phase"] == "baseline_alignment" and degraded_state["phase"] == "network_degradation"
    observed_sim = (
        f"latency {baseline_metrics['latency']}->{degraded_metrics['latency']}; "
        f"jitter {baseline_metrics['jitter']}->{degraded_metrics['jitter']}; "
        f"loss {baseline_metrics['packet_loss']}->{degraded_metrics['packet_loss']}"
    )
    results.append(_result("fault_injection", "Simulator network degradation", "latency, jitter, and loss increase", observed_sim, simulator_passed))

    passed = sum(item.passed for item in results)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "software_version": routes.SOFTWARE_VERSION,
        "catem_version": routes.CATEM_VERSION,
        "api_schema_version": routes.API_SCHEMA_VERSION,
        "repository_commit": _git_commit(),
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "operating_system": platform.platform(),
            "test_framework": "Python standard-library verification harness",
        },
        "api_validation": {
            "serialized_bytes": len(serialized),
            "schema_version": routes.API_SCHEMA_VERSION,
            "required_objects_valid": api_schema_valid,
        },
        "fixtures": {
            "fixture_a": fixture_a.task_type,
            "fixture_b": fixture_b.task_type,
            "fixture_b_sha256": fixture_hash,
            "catem_output_sha256": replay_hashes[0],
            "replay_count": len(replay_hashes),
        },
        "summary": {
            "tests": len(results),
            "passed": passed,
            "failed": len(results) - passed,
        },
        "results": [asdict(item) for item in results],
    }
    return payload


def write_outputs(payload: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "verification_results.json"
    csv_path = output_dir / "verification_results.csv"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["category", "test", "expected", "observed", "passed"])
        writer.writeheader()
        writer.writerows(payload["results"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CATEM software verification and controlled fault injection.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )
    args = parser.parse_args()
    payload = run_verification()
    write_outputs(payload, args.output_dir)
    print(json.dumps(payload["summary"], sort_keys=True))
    print(f"fixture_b_sha256={payload['fixtures']['fixture_b_sha256']}")
    print(f"catem_output_sha256={payload['fixtures']['catem_output_sha256']}")
    return 0 if payload["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
