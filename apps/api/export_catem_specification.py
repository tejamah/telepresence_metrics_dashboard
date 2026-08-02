from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any


API_DIR = Path(__file__).resolve().parent
ROOT = API_DIR.parents[1]
RUNTIME_ROOT = next(
    candidate
    for candidate in (ROOT, API_DIR.parent)
    if (candidate / "services").exists()
)
if str(RUNTIME_ROOT) not in sys.path:
    sys.path.insert(0, str(RUNTIME_ROOT))

import routes


OUTPUT_DIR = (
    ROOT / "catem_latex_paper" / "verification"
    if (ROOT / "catem_latex_paper").exists()
    else ROOT / "reproducibility" / "verification"
)

MEASUREMENT_RECORD_FIELDS = [
    "metric",
    "construct",
    "layer",
    "raw_value",
    "unit",
    "direction",
    "instrument_or_sensor",
    "timestamp",
    "sampling_rate_hz",
    "valid_range",
    "missing",
    "missingness_status",
    "preprocessing",
    "source",
    "provenance",
    "transform_version",
    "interpretation_boundary",
]

RULE_SPECIFICATIONS = [
    {
        "id": "P1",
        "name": "Latency asymmetry",
        "activation": "latency > 90 and agency < ownership",
        "otherwise": "monitor",
    },
    {
        "id": "P2",
        "name": "Presence-performance dissociation",
        "activation": "workload > 70 and presence >= 70 and error_rate > 8",
        "otherwise": "monitor",
    },
    {
        "id": "P3",
        "name": "Assistance trade-off",
        "activation": "autonomy_assistance > 65 and agency < 65",
        "otherwise": "insufficient when assistance is missing; monitor otherwise",
    },
    {
        "id": "P4",
        "name": "Physiological leading indicators",
        "activation": "(hrv < 45 or galvanic_response > 0.65) and (latency > 100 or jitter > 25)",
        "otherwise": "monitor",
    },
    {
        "id": "P5",
        "name": "Synchrony over fidelity",
        "activation": "behavioral_synchrony >= visual_fidelity",
        "otherwise": "monitor",
    },
    {
        "id": "P6",
        "name": "Ethical adaptation",
        "activation": "adaptation_disclosed >= 1 and override_available >= 1 and trust >= 65",
        "otherwise": "at_risk",
    },
]


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_specification() -> dict[str, Any]:
    routes.SESSIONS.clear()
    routes._seed()
    transforms: dict[str, dict[str, Any]] = {}
    for layer, metric_names in routes.CATEM_LAYER_METRICS.items():
        for metric in metric_names:
            transform = dict(routes.METRIC_TRANSFORMS.get(metric, routes.DEFAULT_METRIC_TRANSFORM))
            transforms[metric] = {
                "layer": layer,
                "unit": routes.METRIC_UNITS.get(metric, "instrument_defined"),
                "direction": routes.METRIC_DIRECTIONS.get(metric, "higher_is_better"),
                "valid_range": routes.METRIC_VALID_RANGES.get(metric),
                "transform": transform,
            }
    for metric, registered_transform in routes.METRIC_TRANSFORMS.items():
        if metric in transforms:
            continue
        transforms[metric] = {
            "layer": routes._metric_layer(metric),
            "unit": routes.METRIC_UNITS.get(metric, "instrument_defined"),
            "direction": routes.METRIC_DIRECTIONS.get(metric, "higher_is_better"),
            "valid_range": routes.METRIC_VALID_RANGES.get(metric),
            "transform": dict(registered_transform),
        }

    fixtures = []
    for label, session in zip(("Fixture A", "Fixture B"), routes.SESSIONS):
        fixture = {
            "label": label,
            "synthetic_identifier": session.participant_id,
            "task_type": session.task_type,
            "setup": session.setup,
            "session_time": session.session_time,
            "metrics": session.metrics,
        }
        fixture["sha256"] = _canonical_hash(session.metrics)
        fixtures.append(fixture)

    return {
        "software_version": routes.SOFTWARE_VERSION,
        "catem_version": routes.CATEM_VERSION,
        "api_schema_version": routes.API_SCHEMA_VERSION,
        "layer_schema": routes.CATEM_LAYER_METRICS,
        "layer_interpretation_boundaries": routes.LAYER_INTERPRETATION_BOUNDARIES,
        "measurement_record_schema": {
            "required_fields": MEASUREMENT_RECORD_FIELDS,
            "missing_expected_metrics_are_exported": True,
        },
        "api_response_schema": {
            "required_session_objects": [
                "software_version",
                "api_schema_version",
                "metrics",
                "catem",
                "measurement_records",
            ],
            "required_catem_objects": [
                "framework_version",
                "layers",
                "evidence_profile",
                "propositions",
            ],
            "required_proposition_fields": ["id", "name", "status", "evidence"],
        },
        "transform_registry": transforms,
        "rule_specifications": RULE_SPECIFICATIONS,
        "fixtures": fixtures,
        "event_window_fixture": routes.object_drop_event_window(),
        "interpretation_boundary": (
            "All thresholds and transforms are prototype settings unless an instrument-specific "
            "procedure is explicitly registered. Fixtures are synthetic software-test records."
        ),
    }


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "catem_specification_v0.2.json"
    output_path.write_text(json.dumps(build_specification(), indent=2) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
