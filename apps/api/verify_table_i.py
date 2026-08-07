from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import routes
import verification


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_DIR = ROOT / "catem_short_paper_v55_ieee" / "verification"
DEFAULT_MANUSCRIPT = ROOT / "catem_short_paper_v55_ieee" / "root.tex"
TAGGED_SOURCES = ("apps/api/verification.py", "apps/api/routes.py")


def _git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
    ).strip()


def _source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tagged_sources_unchanged() -> bool:
    result = subprocess.run(
        ["git", "diff", "--quiet", "v0.2.0", "--", *TAGGED_SOURCES],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def _fault_result(base: dict[str, Any], name: str, value: Any) -> dict[str, Any]:
    modified = dict(base)
    modified[name] = value
    return routes.catem_assessment(modified)


def build_table_i_evidence(manuscript_path: Path, output_dir: Path) -> dict[str, Any]:
    # Execute the public harness first and retain its complete machine-readable output.
    harness_payload = verification.run_verification()
    verification.write_outputs(harness_payload, output_dir)

    fixture_b = routes.SESSIONS[1]
    base = dict(fixture_b.metrics)
    baseline_hash_before = verification._canonical_hash(base)
    baseline = routes.catem_assessment(dict(base))

    latency_fault = _fault_result(base, "latency", 220)
    timestamp_fault = _fault_result(base, "timestamp_accuracy", 30)
    tracking_fault = _fault_result(base, "tracking_dropout", 15)
    missing_hrv = dict(base)
    missing_hrv.pop("hrv")
    hrv_fault = routes.catem_assessment(missing_hrv)

    human_metrics = routes.CATEM_LAYER_METRICS["human_state"]
    baseline_hrv_records = sum(name in base for name in human_metrics)
    modified_hrv_records = sum(name in missing_hrv for name in human_metrics)

    rows = [
        {
            "condition": "Latency",
            "input_metric": "latency",
            "input_concept": "end-to-end latency",
            "baseline_input": base["latency"],
            "modified_input": 220,
            "input_unit": "ms",
            "output_metric": "prototype_system_summary",
            "baseline_output": baseline["layers"]["system"]["score"],
            "fault_output": latency_fault["layers"]["system"]["score"],
            "manuscript_left": r"Latency: $82\rightarrow220$~ms",
            "manuscript_right": r"Prototype system summary decreased: $71.2\rightarrow65.0$",
        },
        {
            "condition": "HRV record removed",
            "input_metric": "hrv",
            "input_concept": "expected Human State and Cognition fixture records",
            "baseline_input": baseline_hrv_records,
            "modified_input": modified_hrv_records,
            "input_unit": "records",
            "output_metric": "human_state_coverage",
            "baseline_output": baseline["layers"]["human_state"]["coverage"],
            "fault_output": hrv_fault["layers"]["human_state"]["coverage"],
            "manuscript_left": r"HRV record removed ($8$ expected records $\rightarrow 7$ present)",
            "manuscript_right": r"Human State and Cognition coverage decreased: $100\%\rightarrow87.5\%$",
        },
        {
            "condition": "Timestamp error",
            "input_metric": "timestamp_accuracy",
            "input_concept": "estimated timestamp-alignment error relative to the reference time base",
            "baseline_input": base["timestamp_accuracy"],
            "modified_input": 30,
            "input_unit": "ms_error",
            "output_metric": "synchronization_quality",
            "baseline_output": baseline["evidence_profile"]["synchronization_quality"],
            "fault_output": timestamp_fault["evidence_profile"]["synchronization_quality"],
            "manuscript_left": r"Timestamp error: $3.4\rightarrow30$~ms",
            "manuscript_right": r"Synchronization quality decreased: $75.9\rightarrow54.3$",
        },
        {
            "condition": "Tracking dropout",
            "input_metric": "tracking_dropout",
            "input_concept": "synthetic fixture tracking-dropout input",
            "baseline_input": base["tracking_dropout"],
            "modified_input": 15,
            "input_unit": "%",
            "output_metric": "prototype_system_summary",
            "baseline_output": baseline["layers"]["system"]["score"],
            "fault_output": tracking_fault["layers"]["system"]["score"],
            "manuscript_left": r"Tracking dropout: $4\%\rightarrow15\%$",
            "manuscript_right": r"Prototype system summary decreased: $71.2\rightarrow65.5$",
        },
    ]

    manuscript = manuscript_path.read_text(encoding="utf-8")
    for row in rows:
        row["manuscript_match"] = (
            row["manuscript_left"] in manuscript
            and row["manuscript_right"] in manuscript
        )

    baseline_hash_after = verification._canonical_hash(base)
    raw_faults = {
        item["test"]: item["observed"]
        for item in harness_payload["results"]
        if item["category"] == "fault_injection"
    }
    raw_results_match = (
        raw_faults.get("Increased latency") == "71.2->65.0"
        and raw_faults.get("Missing HRV field") == "100.0->87.5; listed=True"
        and raw_faults.get("Timestamp offset") == "75.9->54.3"
        and raw_faults.get("Increased tracking_dropout") == "71.2->65.5"
    )

    tag_commit = _git("rev-list", "-n", "1", "v0.2.0")
    head_commit = _git("rev-parse", "HEAD")
    tagged_sources_unchanged = _tagged_sources_unchanged()
    baseline_unchanged = (
        baseline_hash_before
        == baseline_hash_after
        == harness_payload["fixtures"]["fixture_b_sha256"]
    )
    required_values_match = (
        base["latency"] == 82
        and base["timestamp_accuracy"] == 3.4
        and tracking_fault["layers"]["system"]["score"] == 65.5
        and len(human_metrics) == 8
        and baseline_hrv_records == 8
    )

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "harness_generated_at": harness_payload["generated_at"],
        "software_version": harness_payload["software_version"],
        "public_tag": "v0.2.0",
        "public_tag_commit": tag_commit,
        "head_commit": head_commit,
        "tagged_harness_and_fixture_sources_unchanged": tagged_sources_unchanged,
        "tagged_source_sha256": {
            relative: _source_sha256(ROOT / relative) for relative in TAGGED_SOURCES
        },
        "baseline_fixture": {
            "name": "Session 2",
            "task_type": fixture_b.task_type,
            "sha256_before_faults": baseline_hash_before,
            "sha256_after_faults": baseline_hash_after,
            "unchanged": baseline_unchanged,
        },
        "raw_harness_summary": harness_payload["summary"],
        "raw_harness_fault_results_match": raw_results_match,
        "required_values": {
            "latency_baseline_ms": base["latency"],
            "timestamp_alignment_error_baseline_ms": base["timestamp_accuracy"],
            "tracking_dropout_fault_output": tracking_fault["layers"]["system"]["score"],
            "hrv_expected_record_count": len(human_metrics),
            "all_match": required_values_match,
        },
        "table_i_rows": rows,
        "table_i_matches_manuscript": all(row["manuscript_match"] for row in rows),
        "verification_passed": bool(
            harness_payload["summary"]["failed"] == 0
            and tag_commit == head_commit
            and tagged_sources_unchanged
            and baseline_unchanged
            and raw_results_match
            and required_values_match
            and all(row["manuscript_match"] for row in rows)
        ),
    }
    return payload


def write_table_i_outputs(payload: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "table_i_verification.json"
    csv_path = output_dir / "table_i_verification.csv"
    json_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    fieldnames = [
        "condition",
        "input_metric",
        "input_concept",
        "baseline_input",
        "modified_input",
        "input_unit",
        "output_metric",
        "baseline_output",
        "fault_output",
        "manuscript_left",
        "manuscript_right",
        "manuscript_match",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(payload["table_i_rows"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Regenerate and verify the CATEM Table I evidence from Session 2."
    )
    parser.add_argument("--manuscript", type=Path, default=DEFAULT_MANUSCRIPT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    payload = build_table_i_evidence(args.manuscript, args.output_dir)
    write_table_i_outputs(payload, args.output_dir)
    print(json.dumps({
        "verification_passed": payload["verification_passed"],
        "required_values": payload["required_values"],
        "table_i_matches_manuscript": payload["table_i_matches_manuscript"],
    }, sort_keys=True))
    return 0 if payload["verification_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
