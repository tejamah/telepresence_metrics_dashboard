from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import statistics
import sys
import time
import tracemalloc
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


API_DIR = Path(__file__).resolve().parent
RUNTIME_ROOT = next(
    candidate
    for candidate in (API_DIR.parents[1], API_DIR.parent)
    if (candidate / "services").exists()
)
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

import routes


DEFAULT_OUTPUT_DIR = (
    RUNTIME_ROOT / "catem_latex_paper" / "verification"
    if (RUNTIME_ROOT / "catem_latex_paper").exists()
    else RUNTIME_ROOT / "verification"
)


def _percentile(sorted_values: list[float], percentile: float) -> float:
    if not sorted_values:
        return 0.0
    index = max(0, min(len(sorted_values) - 1, math.ceil(percentile * len(sorted_values)) - 1))
    return sorted_values[index]


def _timed(
    function: Callable[[], Any],
    *,
    iterations: int,
    warmup: int,
    cleanup: Callable[[], None] | None = None,
) -> tuple[dict[str, float | int], Any]:
    result: Any = None
    for _ in range(warmup):
        result = function()
        if cleanup:
            cleanup()

    durations_ms: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter_ns()
        result = function()
        elapsed = time.perf_counter_ns() - start
        durations_ms.append(elapsed / 1_000_000)
        if cleanup:
            cleanup()

    ordered = sorted(durations_ms)
    mean_ms = statistics.fmean(durations_ms)
    return {
        "iterations": iterations,
        "mean_ms": round(mean_ms, 6),
        "median_ms": round(statistics.median(durations_ms), 6),
        "p95_ms": round(_percentile(ordered, 0.95), 6),
        "p99_ms": round(_percentile(ordered, 0.99), 6),
        "min_ms": round(ordered[0], 6),
        "max_ms": round(ordered[-1], 6),
        "throughput_per_second": round(1000 / mean_ms, 2) if mean_ms else 0,
    }, result


def _peak_traced_bytes(
    function: Callable[[], Any],
    *,
    iterations: int = 100,
    cleanup: Callable[[], None] | None = None,
) -> int:
    tracemalloc.start()
    for _ in range(iterations):
        function()
        if cleanup:
            cleanup()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def run_benchmark(iterations: int, warmup: int) -> dict[str, Any]:
    routes.SESSIONS.clear()
    routes.TELEMETRY_STREAM.clear()
    routes._seed()
    fixture = routes.SESSIONS[-1]
    metrics = dict(fixture.metrics)
    telemetry_event = routes.TelemetryEvent(
        participant_id=fixture.participant_id,
        source="in_process_benchmark",
        timestamp="2026-07-01T14:32:18.240Z",
        metrics=metrics,
    )

    cases: list[tuple[str, Callable[[], Any], Callable[[], None] | None]] = [
        ("catem_assessment", lambda: routes.catem_assessment(dict(metrics)), None),
        ("full_session_response", lambda: routes._session_response(fixture), None),
        (
            "telemetry_ingestion_response",
            lambda: routes.ingest_telemetry(telemetry_event),
            routes.TELEMETRY_STREAM.clear,
        ),
    ]

    results: list[dict[str, Any]] = []
    for name, function, cleanup in cases:
        timing, result = _timed(function, iterations=iterations, warmup=warmup, cleanup=cleanup)
        serialized_bytes = len(json.dumps(result, sort_keys=True, separators=(",", ":")).encode("utf-8"))
        peak_bytes = _peak_traced_bytes(function, cleanup=cleanup)
        results.append({
            "operation": name,
            **timing,
            "serialized_response_bytes": serialized_bytes,
            "peak_traced_allocation_bytes_100_iterations": peak_bytes,
        })

    routes.TELEMETRY_STREAM.clear()
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "single-process in-memory Python function benchmark; excludes HTTP transport, WebSocket I/O, browser rendering, persistent storage, and concurrent clients",
        "environment": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "operating_system": platform.platform(),
            "machine": platform.machine(),
            "processor": platform.processor() or "not_reported",
        },
        "software": {
            "software_version": routes.SOFTWARE_VERSION,
            "catem_version": routes.CATEM_VERSION,
            "api_schema_version": routes.API_SCHEMA_VERSION,
        },
        "configuration": {
            "warmup_iterations": warmup,
            "measured_iterations_per_operation": iterations,
            "memory_iterations_per_operation": 100,
            "fixture": fixture.participant_id,
        },
        "results": results,
        "interpretation_boundary": "Results characterize this machine and process only. They are not a network capacity, multi-user scalability, deadline-safety, or deployment benchmark.",
    }


def write_outputs(payload: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "performance_benchmark.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    fields = [
        "operation", "iterations", "mean_ms", "median_ms", "p95_ms", "p99_ms",
        "min_ms", "max_ms", "throughput_per_second", "serialized_response_bytes",
        "peak_traced_allocation_bytes_100_iterations",
    ]
    with (output_dir / "performance_benchmark.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(payload["results"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark CATEM in-process processing operations.")
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--warmup", type=int, default=200)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    if args.iterations < 1 or args.warmup < 0:
        parser.error("iterations must be positive and warmup must be nonnegative")
    payload = run_benchmark(args.iterations, args.warmup)
    write_outputs(payload, args.output_dir)
    print(json.dumps(payload["results"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
