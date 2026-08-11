from __future__ import annotations

import asyncio
import copy
import csv
import io
import math
import platform
import statistics
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from services.telemetry import TelemetrySimulator

router = APIRouter()

SOFTWARE_VERSION = "0.2.0"
CATEM_VERSION = "catem-0.2"
API_SCHEMA_VERSION = "2026-07"

OBJECT_DROP_EVENT = {
    "event_id": "object-drop-001",
    "participant_id": "SYNTH-EVENT-001",
    "task_type": "Remote object transfer",
    "event_name": "Robot object drop",
    "reference_time_seconds": 0,
    "window_seconds": [-2, 2],
    "synthetic": True,
    "samples": [
        {
            "offset_seconds": -2,
            "metrics": {
                "latency": 96.0,
                "packet_loss": 1.2,
                "tracking_dropout": 2.0,
                "workload": 58.0,
                "heart_rate": 88.0,
                "agency": 78.0,
                "task_error": 0.0,
            },
        },
        {
            "offset_seconds": -1,
            "metrics": {
                "latency": 118.0,
                "packet_loss": 2.4,
                "tracking_dropout": 3.0,
                "workload": 64.0,
                "heart_rate": 96.0,
                "agency": 72.0,
                "task_error": 0.0,
            },
        },
        {
            "offset_seconds": 0,
            "metrics": {
                "latency": 220.0,
                "packet_loss": 12.0,
                "tracking_dropout": 15.0,
                "workload": 82.0,
                "heart_rate": 112.0,
                "agency": 58.0,
                "task_error": 1.0,
            },
        },
        {
            "offset_seconds": 1,
            "metrics": {
                "latency": 154.0,
                "packet_loss": 5.1,
                "tracking_dropout": 8.0,
                "workload": 72.0,
                "heart_rate": 104.0,
                "agency": 64.0,
                "task_error": 0.0,
            },
        },
        {
            "offset_seconds": 2,
            "metrics": {
                "latency": 108.0,
                "packet_loss": 1.9,
                "tracking_dropout": 3.0,
                "workload": 62.0,
                "heart_rate": 93.0,
                "agency": 72.0,
                "task_error": 0.0,
            },
        },
    ],
}

EVENT_METRIC_METADATA = {
    "agency": {"layer": "experience", "unit": "instrument_defined", "source": "interface_agency_fixture"},
    "task_error": {"layer": "action", "unit": "binary", "source": "robot_task_log_fixture"},
    "workload": {"layer": "human_state", "unit": "%", "source": "workload_instrument_fixture"},
    "heart_rate": {"layer": "human_state", "unit": "bpm", "source": "physiology_sensor_fixture"},
    "latency": {"layer": "system", "unit": "ms", "source": "network_telemetry_fixture"},
    "packet_loss": {"layer": "system", "unit": "%", "source": "network_telemetry_fixture"},
    "tracking_dropout": {"layer": "system", "unit": "%", "source": "tracking_telemetry_fixture"},
}


METRIC_WEIGHTS = {
    "embodiment": 0.2,
    "presence": 0.18,
    "performance": 0.18,
    "behavior": 0.12,
    "physiological": 0.12,
    "system": 0.14,
    "visualization": 0.06,
}

CATEM_LAYER_METRICS = {
    "experience": [
        "ownership", "agency", "self_location", "presence", "social_presence",
        "trust", "usability",
    ],
    "action": [
        "task_efficiency", "task_completion_time", "error_rate", "path_efficiency",
        "collaboration_quality", "movement_smoothness",
    ],
    "human_state": [
        "workload", "situation_awareness", "heart_rate", "hrv", "galvanic_response",
        "cybersickness", "comfort", "fatigue",
    ],
    "system": [
        "latency", "jitter", "fps", "packet_loss", "tracking_dropout",
        "calibration_error", "haptic_delay",
    ],
    "data_interpretation": [
        "timestamp_accuracy", "missing_data_percent", "fusion_latency",
        "sampling_sync", "visualization_clarity", "explanation_satisfaction",
    ],
}

METRIC_UNITS = {
    "task_completion_time": "s",
    "error_rate": "%",
    "workload": "%",
    "heart_rate": "bpm",
    "hrv": "ms",
    "galvanic_response": "normalized",
    "cybersickness": "instrument_score",
    "latency": "ms",
    "jitter": "ms",
    "fps": "frames_per_second",
    "packet_loss": "%",
    "tracking_dropout": "%",
    "calibration_error": "platform_defined",
    "haptic_delay": "ms",
    "timestamp_accuracy": "ms_error",
    "missing_data_percent": "%",
    "fusion_latency": "ms",
    "conversational_latency": "ms",
}

METRIC_DIRECTIONS = {
    "task_completion_time": "lower_is_better",
    "error_rate": "lower_is_better",
    "safety_events": "lower_is_better",
    "workload": "instrument_dependent",
    "heart_rate": "context_dependent",
    "hrv": "context_dependent",
    "galvanic_response": "context_dependent",
    "cybersickness": "lower_is_better",
    "fatigue": "lower_is_better",
    "latency": "lower_is_better",
    "jitter": "lower_is_better",
    "fps": "higher_is_better",
    "packet_loss": "lower_is_better",
    "tracking_dropout": "lower_is_better",
    "calibration_error": "lower_is_better",
    "haptic_delay": "lower_is_better",
    "timestamp_accuracy": "lower_error_is_better",
    "missing_data_percent": "lower_is_better",
    "fusion_latency": "lower_is_better",
}

METRIC_VALID_RANGES = {
    "error_rate": [0, 100],
    "workload": [0, 100],
    "heart_rate": [20, 240],
    "hrv": [0, 250],
    "galvanic_response": [0, 1],
    "latency": [0, None],
    "jitter": [0, None],
    "fps": [0, None],
    "packet_loss": [0, 100],
    "tracking_dropout": [0, 100],
    "missing_data_percent": [0, 100],
}

# Every non-default transform is registered explicitly. Parameters remain
# prototype settings unless an instrument-specific scoring procedure is cited.
METRIC_TRANSFORMS: dict[str, dict[str, Any]] = {
    "task_completion_time": {"type": "negative_piecewise", "low": 45, "high": 240},
    "error_rate": {"type": "negative_piecewise", "low": 2, "high": 25},
    "safety_events": {"type": "negative_piecewise", "low": 0, "high": 6},
    "heart_rate": {"type": "negative_piecewise", "low": 70, "high": 120},
    "latency": {"type": "negative_piecewise", "low": 30, "high": 180},
    "packet_loss": {"type": "negative_piecewise", "low": 0.5, "high": 8},
    "haptic_delay": {"type": "negative_piecewise", "low": 20, "high": 220},
    "jitter": {"type": "negative_piecewise", "low": 5, "high": 60},
    "tracking_dropout": {"type": "negative_piecewise", "low": 0, "high": 10},
    "calibration_error": {"type": "negative_piecewise", "low": 0.5, "high": 8},
    "cybersickness": {"type": "negative_piecewise", "low": 5, "high": 70},
    "fatigue": {"type": "negative_piecewise", "low": 10, "high": 85},
    "missing_data_percent": {"type": "negative_piecewise", "low": 0, "high": 20},
    "fusion_latency": {"type": "negative_piecewise", "low": 10, "high": 180},
    "fps": {"type": "ratio_clamped", "reference": 90, "minimum": 20, "maximum": 100},
    "timestamp_accuracy": {"type": "linear_penalty", "intercept": 100, "slope": 4},
}

DEFAULT_METRIC_TRANSFORM = {
    "type": "positive_piecewise",
    "low": 45,
    "high": 75,
    "threshold_source": "prototype_setting",
}
for _transform in METRIC_TRANSFORMS.values():
    _transform["threshold_source"] = "prototype_setting"

LAYER_INTERPRETATION_BOUNDARIES = {
    "experience": "Experience measures do not establish task success, safety, or physiological stability.",
    "action": "Task outcomes remain task- and assistance-specific and do not establish agency or trust.",
    "human_state": "Human-state and cognition indicators require instrument definitions, baselines, artifact control, and context.",
    "system": "System-condition measures require end-to-end definitions and time alignment with human outcomes.",
    "data_interpretation": "Data and interpretation conditions do not establish construct validity or truth of an inference.",
    "unassigned": "The metric is preserved but requires an explicit construct and layer assignment.",
}

HIGHER_IS_BETTER = {
    "embodiment": True,
    "ownership": True,
    "agency": True,
    "presence": True,
    "task_efficiency": True,
    "task_completion_time": False,
    "error_rate": False,
    "safety_events": False,
    "workload": False,
    "collaboration_quality": True,
    "heart_rate": False,
    "hrv": True,
    "latency": False,
    "fps": True,
    "packet_loss": False,
    "visual_match": True,
    "haptic_delay": False,
}


class ExperimentSession(BaseModel):
    participant_id: str = Field(..., min_length=1)
    task_type: str = Field(default="Remote manipulation")
    setup: str = Field(default="VR telepresence")
    session_time: str | None = None
    metrics: dict[str, float] = Field(default_factory=dict)


class TelemetryEvent(BaseModel):
    session_id: int | None = None
    participant_id: str
    source: str = Field(default="simulator")
    timestamp: str | None = None
    metrics: dict[str, float] = Field(default_factory=dict)


@dataclass
class StoredSession:
    id: int
    participant_id: str
    task_type: str
    setup: str
    session_time: str
    metrics: dict[str, float]
    scores: dict[str, Any] = field(default_factory=dict)
    insight: str = ""


SESSIONS: list[StoredSession] = []
TELEMETRY_STREAM: list[dict[str, Any]] = []
SIMULATOR = TelemetrySimulator()


def _numeric(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _score_positive(value: float, low: float = 45, high: float = 75) -> float:
    if value <= low:
        return max(0, value * 0.7)
    if value >= high:
        return min(100, 75 + (value - high) * 0.5)
    return 40 + ((value - low) / (high - low)) * 35


def _score_negative(value: float, low: float, high: float) -> float:
    if value <= low:
        return 92
    if value >= high:
        return 25
    return 92 - ((value - low) / (high - low)) * 67


def _metric_score(name: str, value: float) -> float:
    transform = METRIC_TRANSFORMS.get(name, DEFAULT_METRIC_TRANSFORM)
    transform_type = transform["type"]
    if transform_type == "negative_piecewise":
        return _score_negative(value, transform["low"], transform["high"])
    if transform_type == "ratio_clamped":
        return min(
            transform["maximum"],
            max(transform["minimum"], (value / transform["reference"]) * 100),
        )
    if transform_type == "linear_penalty":
        return min(100, max(0, transform["intercept"] - value * transform["slope"]))
    return _score_positive(value, transform["low"], transform["high"])


def _grade(score: float) -> str:
    if score >= 75:
        return "high"
    if score >= 50:
        return "medium"
    return "low"


def _metric_layer(name: str) -> str:
    for layer, metric_names in CATEM_LAYER_METRICS.items():
        if name in metric_names:
            return layer
    return "unassigned"


def measurement_contract(
    metrics: dict[str, float],
    *,
    timestamp: str | None,
    source: str,
) -> list[dict[str, Any]]:
    """Return an inspectable record for every expected or supplied metric.

    Records preserve raw values and missingness. Instrument-specific sampling,
    preprocessing, and reliability evidence remain explicitly unreported until
    supplied by an acquisition adapter or study protocol.
    """
    expected = {name for names in CATEM_LAYER_METRICS.values() for name in names}
    names = sorted(expected | set(metrics))
    records: list[dict[str, Any]] = []
    for name in names:
        layer = _metric_layer(name)
        missing = name not in metrics or metrics.get(name) is None
        records.append(
            {
                "metric": name,
                "construct": name.replace("_", " "),
                "layer": layer,
                "raw_value": None if missing else metrics[name],
                "unit": METRIC_UNITS.get(name, "instrument_defined"),
                "direction": METRIC_DIRECTIONS.get(name, "higher_is_better"),
                "instrument_or_sensor": "not_reported",
                "timestamp": timestamp,
                "sampling_rate_hz": None,
                "valid_range": METRIC_VALID_RANGES.get(name),
                "missing": missing,
                "missingness_status": "missing" if missing else "observed",
                "preprocessing": "none_declared",
                "source": source,
                "provenance": f"{source}:raw_metric",
                "transform_version": CATEM_VERSION,
                "interpretation_boundary": LAYER_INTERPRETATION_BOUNDARIES[layer],
            }
        )
    return records


def calculate_scores(metrics: dict[str, float]) -> dict[str, Any]:
    category_map = {
        "embodiment": ["embodiment", "ownership", "agency"],
        "presence": ["presence"],
        "performance": ["task_efficiency", "task_completion_time", "error_rate"],
        "behavior": ["safety_events", "workload", "collaboration_quality"],
        "physiological": ["heart_rate", "hrv"],
        "system": ["latency", "fps", "packet_loss", "haptic_delay"],
        "visualization": ["visual_match"],
    }

    categories: dict[str, dict[str, Any]] = {}
    for category, metric_names in category_map.items():
        values = [
            _metric_score(name, metrics[name])
            for name in metric_names
            if name in metrics and metrics[name] is not None
        ]
        score = round(statistics.mean(values), 1) if values else 0
        categories[category] = {"score": score, "level": _grade(score)}

    overall = round(
        sum(categories[name]["score"] * weight for name, weight in METRIC_WEIGHTS.items()),
        1,
    )

    return {
        "categories": categories,
        "overall": overall,
        "overall_level": _grade(overall),
    }


def catem_assessment(metrics: dict[str, float]) -> dict[str, Any]:
    layers: dict[str, dict[str, Any]] = {}
    present_count = 0
    expected_count = sum(len(names) for names in CATEM_LAYER_METRICS.values())

    for layer, metric_names in CATEM_LAYER_METRICS.items():
        present = [name for name in metric_names if name in metrics]
        present_count += len(present)
        score = round(statistics.mean(_metric_score(name, metrics[name]) for name in present), 1) if present else 0
        layers[layer] = {
            "score": score,
            "level": _grade(score),
            "coverage": round(len(present) / len(metric_names) * 100, 1),
            "present_metrics": present,
            "missing_metrics": [name for name in metric_names if name not in metrics],
        }

    coverage = round(present_count / expected_count * 100, 1)
    sync_score = round(statistics.mean([
        _metric_score("timestamp_accuracy", metrics.get("timestamp_accuracy", 8)),
        _metric_score("missing_data_percent", metrics.get("missing_data_percent", 8)),
        _metric_score("fusion_latency", metrics.get("fusion_latency", 90)),
        _metric_score("sampling_sync", metrics.get("sampling_sync", 60)),
    ]), 1)
    evidence_profile = {
        "field_coverage": coverage,
        "synchronization_quality": sync_score,
        "missing_data_burden": metrics.get("missing_data_percent"),
        "provenance_completeness": None,
        "reliability_evidence": None,
    }

    latency = metrics.get("latency", 0)
    agency = metrics.get("agency", 100)
    ownership = metrics.get("ownership", 100)
    workload = metrics.get("workload", 0)
    error_rate = metrics.get("error_rate", 0)
    presence = metrics.get("presence", 0)
    autonomy = metrics.get("autonomy_assistance", 0)
    trust = metrics.get("trust", 70)
    hrv = metrics.get("hrv", 60)
    gsr = metrics.get("galvanic_response", 0.3)
    social_sync = statistics.mean([
        metrics.get("gaze_alignment", 70),
        metrics.get("gesture_timing", 70),
        max(0, 100 - metrics.get("conversational_latency", 150) / 4),
    ])
    visual_fidelity = metrics.get("avatar_fidelity", metrics.get("visual_match", 70))

    propositions = [
        {
            "id": "P1",
            "name": "Latency asymmetry",
            "status": "observed" if latency > 90 and agency < ownership else "monitor",
            "evidence": f"{latency:.0f} ms latency; agency {agency:.0f}; ownership {ownership:.0f}",
        },
        {
            "id": "P2",
            "name": "Presence–performance dissociation",
            "status": "observed" if workload > 70 and presence >= 70 and error_rate > 8 else "monitor",
            "evidence": f"presence {presence:.0f}; workload {workload:.0f}; errors {error_rate:.1f}%",
        },
        {
            "id": "P3",
            "name": "Assistance trade-off",
            "status": "observed" if autonomy > 65 and agency < 65 else "insufficient" if "autonomy_assistance" not in metrics else "monitor",
            "evidence": f"assistance {autonomy:.0f}; agency {agency:.0f}; trust {trust:.0f}",
        },
        {
            "id": "P4",
            "name": "Physiological leading indicators",
            "status": "observed" if (hrv < 45 or gsr > 0.65) and (latency > 100 or metrics.get("jitter", 0) > 25) else "monitor",
            "evidence": f"HRV {hrv:.0f} ms; GSR {gsr:.2f}; jitter {metrics.get('jitter', 0):.0f} ms",
        },
        {
            "id": "P5",
            "name": "Synchrony over fidelity",
            "status": "observed" if social_sync >= visual_fidelity else "monitor",
            "evidence": f"behavioral synchrony {social_sync:.0f}; avatar fidelity {visual_fidelity:.0f}",
        },
        {
            "id": "P6",
            "name": "Ethical adaptation",
            "status": "supported" if metrics.get("adaptation_disclosed", 0) >= 1 and metrics.get("override_available", 0) >= 1 and trust >= 65 else "at_risk",
            "evidence": f"disclosed {bool(metrics.get('adaptation_disclosed', 0))}; overridable {bool(metrics.get('override_available', 0))}; trust {trust:.0f}",
        },
    ]

    return {
        "framework": "Cross-Layer Adaptive Telepresence Evaluation Model",
        "framework_version": CATEM_VERSION,
        "layers": layers,
        "evidence_profile": evidence_profile,
        "propositions": propositions,
        "adaptive_recommendations": [
            "Reduce rendering complexity and protect agency." if latency > 100 else "Maintain the current rendering profile.",
            "Prompt a workload check and preserve user override." if workload > 70 else "Continue monitoring workload.",
            "Disclose adaptation logic before intervention." if metrics.get("adaptation_disclosed", 0) < 1 else "Adaptation disclosure is active.",
        ],
    }


def object_drop_event_window() -> dict[str, Any]:
    """Return the canonical, traceable five-sample event fixture used in the papers."""
    payload = copy.deepcopy(OBJECT_DROP_EVENT)
    records: list[dict[str, Any]] = []
    for sample in payload["samples"]:
        offset = sample["offset_seconds"]
        for metric, value in sample["metrics"].items():
            metadata = EVENT_METRIC_METADATA[metric]
            records.append(
                {
                    "metric": metric,
                    "construct": metric.replace("_", " "),
                    "layer": metadata["layer"],
                    "raw_value": value,
                    "unit": metadata["unit"],
                    "offset_seconds": offset,
                    "event_id": payload["event_id"],
                    "missing": False,
                    "source": metadata["source"],
                    "provenance": "authored deterministic software-test fixture",
                    "transform_version": SOFTWARE_VERSION,
                    "interpretation_boundary": (
                        "Synthetic event-window value for interface and alignment verification; "
                        "not a participant observation or causal estimate."
                    ),
                }
            )
    payload.update(
        {
            "software_version": SOFTWARE_VERSION,
            "catem_version": CATEM_VERSION,
            "api_schema_version": API_SCHEMA_VERSION,
            "records": records,
            "interpretation_boundary": (
                "The five samples are deterministic authored values for software verification. "
                "Temporal co-occurrence does not establish causality."
            ),
        }
    )
    return payload


def generate_insight(session: StoredSession) -> str:
    metrics = session.metrics
    scores = session.scores["categories"]
    clauses: list[str] = []

    if metrics.get("agency", 0) >= 75 and metrics.get("ownership", 100) < 60:
        clauses.append("strong agency but reduced ownership, alongside visual mismatch or delayed feedback")
    if metrics.get("latency", 0) > 100:
        clauses.append("high latency alongside lower presence or agency")
    if metrics.get("workload", 0) > 70 and metrics.get("error_rate", 0) > 10:
        clauses.append("high workload is paired with elevated error rates")
    if scores["embodiment"]["score"] >= 75 and scores["performance"]["score"] >= 70:
        clauses.append("elevated embodiment and task-performance summaries occurring together")
    if metrics.get("heart_rate", 0) > 110 or metrics.get("hrv", 100) < 40:
        clauses.append("physiological values crossing the prototype stress-or-fatigue rule threshold")
    if not clauses:
        clauses.append("the session shows balanced telepresence quality with no dominant risk signal")

    return f"Session {session.participant_id} showed {', and '.join(clauses)}."


def detect_risks(metrics: dict[str, float]) -> list[dict[str, Any]]:
    rules = [
        ("unstable sensor pipeline", metrics.get("packet_loss", 0) > 5, "packet loss exceeds the prototype synchronization-rule threshold"),
        ("synchronization failure", metrics.get("latency", 0) > 150, "network or rendering delay exceeds the prototype rule threshold"),
        ("embodiment degradation", metrics.get("agency", 100) < 55 or metrics.get("ownership", 100) < 55, "agency or ownership is below the prototype rule threshold"),
        ("cognitive overload", metrics.get("workload", 0) > 80 or metrics.get("heart_rate", 0) > 115, "the rule-based workload or physiology flag is active"),
        ("unsafe control condition", metrics.get("safety_events", 0) >= 3, "repeated safety events require experiment review"),
    ]
    return [
        {"type": name, "severity": "high" if "unsafe" in name or "failure" in name else "medium", "detail": detail}
        for name, active, detail in rules
        if active
    ]


def predict_embodiment_state(metrics: dict[str, float]) -> dict[str, Any]:
    embodiment = _metric_score("embodiment", metrics.get("embodiment", 65))
    agency = _metric_score("agency", metrics.get("agency", 65))
    ownership = _metric_score("ownership", metrics.get("ownership", 65))
    latency_penalty = max(0, min(35, (metrics.get("latency", 40) - 40) * 0.18))
    stress_penalty = max(0, min(20, (metrics.get("workload", 50) - 55) * 0.25))
    quality = round(max(0, min(100, statistics.mean([embodiment, agency, ownership]) - latency_penalty - stress_penalty)), 1)
    breakdown_probability = round(max(0, min(1, (100 - quality) / 100)), 2)
    return {
        "predicted_embodiment_quality": quality,
        "immersion_breakdown_probability": breakdown_probability,
        "state": "stable" if quality >= 70 else "at_risk" if quality >= 50 else "degraded",
    }


def explain_prediction(metrics: dict[str, float]) -> list[dict[str, Any]]:
    factors = [
        ("latency", metrics.get("latency", 0), 90, "latency exceeds the prototype rule threshold"),
        ("fps", metrics.get("fps", 90), 55, "frame rate is below the prototype rule threshold"),
        ("packet_loss", metrics.get("packet_loss", 0), 3, "packet loss exceeds the prototype rule threshold"),
        ("heart_rate", metrics.get("heart_rate", 80), 105, "physiology exceeds the prototype stress-flag threshold"),
        ("workload", metrics.get("workload", 50), 70, "workload exceeds the prototype overload-flag threshold"),
        ("agency", metrics.get("agency", 100), 60, "agency is below the prototype rule threshold"),
    ]
    explanations = []
    for name, value, threshold, detail in factors:
        active = value > threshold if name not in {"fps", "agency"} else value < threshold
        if active:
            impact = min(1, abs(value - threshold) / max(threshold, 1))
            explanations.append({"factor": name, "value": value, "impact": round(impact, 2), "detail": detail})
    return explanations


def cognitive_state(metrics: dict[str, float]) -> dict[str, Any]:
    latency_load = min(30, max(0, (metrics.get("latency", 40) - 50) * 0.18))
    physiology_load = min(25, max(0, (metrics.get("heart_rate", 80) - 85) * 0.4))
    workload_load = min(25, max(0, (metrics.get("workload", 45) - 45) * 0.45))
    agency_buffer = min(20, max(0, (metrics.get("agency", 70) - 50) * 0.35))
    stability = round(max(0, min(100, 86 - latency_load - physiology_load - workload_load + agency_buffer)), 1)
    collapse_risk = round(max(0, min(100, 100 - stability + max(0, metrics.get("packet_loss", 0) - 2) * 4)), 1)
    attention_drift = round(max(0, min(100, metrics.get("workload", 45) * 0.45 + max(0, metrics.get("fps", 90) - 90) * -0.1)), 1)
    return {
        "cognitive_stability": stability,
        "immersion_collapse_risk": "high" if collapse_risk >= 70 else "medium" if collapse_risk >= 40 else "low",
        "collapse_risk_score": collapse_risk,
        "attention_drift": attention_drift,
        "stress_escalation": "elevated" if physiology_load > 12 or workload_load > 14 else "nominal",
    }


def failure_forecast(metrics: dict[str, float]) -> dict[str, Any]:
    risk_score = (
        max(0, metrics.get("latency", 40) - 80) * 0.25
        + metrics.get("packet_loss", 0) * 4
        + max(0, metrics.get("workload", 50) - 60) * 0.45
        + max(0, 65 - metrics.get("agency", 75)) * 0.6
    )
    rule_activation_score = round(max(0, min(100, risk_score)), 1)
    rule_status = "elevated" if risk_score >= 35 else "nominal"
    return {
        "prediction": "not_estimated",
        "time_to_event_seconds": None,
        "confidence": None,
        "rule_status": rule_status,
        "rule_activation_score": rule_activation_score,
        "review_prompts": [
            "review rendering settings" if metrics.get("fps", 90) < 60 else "retain current rendering settings",
            "review network conditions" if metrics.get("latency", 0) > 100 else "retain current network settings",
            "review workload and haptic settings" if metrics.get("workload", 0) > 75 else "retain current haptic settings",
        ],
        "interpretation_boundary": (
            "Deterministic threshold review only; no event time, probability, predictive accuracy, "
            "diagnosis, or causal effect is estimated."
        ),
    }


def embodied_consciousness(metrics: dict[str, float]) -> dict[str, Any]:
    cognitive = cognitive_state(metrics)
    embodiment = predict_embodiment_state(metrics)
    awareness = round(min(100, max(0, cognitive["cognitive_stability"] * 0.55 + metrics.get("presence", 65) * 0.45)), 1)
    attention = round(max(0, min(100, 100 - cognitive["attention_drift"])), 1)
    control_confidence = round(
        max(0, min(100, metrics.get("agency", 65) * 0.5 + embodiment["predicted_embodiment_quality"] * 0.5)),
        1,
    )
    adaptation = round(max(0, min(100, 100 - cognitive["collapse_risk_score"] * 0.55)), 1)
    continuity = round(statistics.mean([awareness, attention, control_confidence, adaptation]), 1)
    return {
        "awareness": awareness,
        "attention": attention,
        "control_confidence": control_confidence,
        "adaptation": adaptation,
        "presence_continuity": continuity,
        "state": "integrated" if continuity >= 72 else "fragmenting" if continuity >= 52 else "collapsed",
    }


def human_digital_twin(participant_id: str, metrics: dict[str, float]) -> dict[str, Any]:
    baseline_hr = 82
    baseline_workload = 48
    fatigue = round(max(0, min(100, (metrics.get("heart_rate", baseline_hr) - baseline_hr) * 1.2 + metrics.get("workload", 50) * 0.45)), 1)
    adaptation_profile = "fast adapter" if metrics.get("agency", 0) >= 78 else "needs reinforcement" if metrics.get("ownership", 100) < 60 else "steady operator"
    fingerprint = {
        "latency_sensitivity": "high" if metrics.get("latency", 0) > 110 and metrics.get("agency", 100) < 75 else "moderate",
        "stress_trigger": "workload" if metrics.get("workload", 0) > baseline_workload + 20 else "network instability",
        "recovery_strategy": "haptic reinforcement" if metrics.get("ownership", 100) < 65 else "visual stabilization",
    }
    return {
        "participant_id": participant_id,
        "physiological_baseline": {"heart_rate": baseline_hr, "workload": baseline_workload},
        "fatigue_index": fatigue,
        "adaptation_profile": adaptation_profile,
        "embodiment_fingerprint": fingerprint,
    }


def embodied_memory_graph(metrics: dict[str, float]) -> dict[str, Any]:
    triggers = []
    recoveries = []
    if metrics.get("latency", 0) > 100:
        triggers.append("latency spike")
        recoveries.append("adaptive compression")
    if metrics.get("workload", 0) > 70:
        triggers.append("cognitive overload")
        recoveries.append("robot speed reduction")
    if metrics.get("ownership", 100) < 65:
        triggers.append("ownership drift")
        recoveries.append("haptic reinforcement")
    if metrics.get("fps", 90) < 60:
        triggers.append("visual instability")
        recoveries.append("rendering simplification")
    return {
        "past_failure_patterns": triggers or ["no dominant failure pattern"],
        "successful_recovery_strategies": recoveries or ["maintain current control envelope"],
        "memory_strength": min(100, 40 + len(triggers) * 18),
    }


def telepresence_language_model(metrics: dict[str, float]) -> dict[str, Any]:
    consciousness = embodied_consciousness(metrics)
    forecast = failure_forecast(metrics)
    explanation = explain_prediction(metrics)
    top_factor = explanation[0]["factor"] if explanation else "stable multimodal alignment"
    return {
        "latent_state": consciousness["state"],
        "reasoning_trace": [
            f"presence continuity is {consciousness['presence_continuity']}%",
            f"dominant explanatory signal: {top_factor}",
            f"rule status: {forecast['rule_status']}",
        ],
        "adaptive_decision": forecast["review_prompts"],
        "research_sentence": (
            f"Heuristic state label: {consciousness['state']}. "
            f"The {forecast['rule_status']} descriptive rule condition flags {top_factor} for review."
        ),
    }


def reality_sync_state(metrics: dict[str, float]) -> dict[str, Any]:
    network_sync = max(0, 100 - max(0, metrics.get("latency", 40) - 40) * 0.35 - metrics.get("packet_loss", 0) * 4)
    visual_sync = min(100, metrics.get("fps", 75) * 1.1)
    body_sync = statistics.mean([metrics.get("agency", 65), metrics.get("ownership", 65), metrics.get("presence", 65)])
    physiological_sync = max(0, 100 - max(0, metrics.get("heart_rate", 80) - 85) * 0.8)
    unified = round(statistics.mean([network_sync, visual_sync, body_sync, physiological_sync]), 1)
    return {
        "physical_robot_sync": round(network_sync, 1),
        "vr_world_sync": round(visual_sync, 1),
        "body_state_sync": round(body_sync, 1),
        "physiological_stream_sync": round(physiological_sync, 1),
        "unified_reality_score": unified,
        "orchestration_state": "locked" if unified >= 75 else "drifting" if unified >= 55 else "desynchronized",
    }


def autonomous_scientist(metrics: dict[str, float]) -> dict[str, Any]:
    hypothesis = "Hypothesis: Latency above 120ms may be associated with reduced ownership and agency during embodied teleoperation."
    suggested_experiment = "Test this using counterbalanced trials at 40ms, 80ms, 120ms, and 160ms latency with synchronized HRV, gaze, task errors, and ownership ratings."
    if metrics.get("workload", 0) > 75:
        hypothesis = "Hypothesis: Cognitive workload may be associated with network instability and task errors."
    if metrics.get("ownership", 100) < 60:
        hypothesis = "Hypothesis: Visual-haptic mismatch may be associated with reduced ownership."
        suggested_experiment = "Test this using counterbalanced visual-haptic mismatch conditions with synchronized ownership ratings."
    return {
        "observed": telepresence_language_model(metrics)["research_sentence"],
        "hypothesis": hypothesis,
        "suggested_experiment": suggested_experiment,
        "analysis_plan": ["Pearson/Spearman correlation", "repeated-measures ANOVA", "mixed-effects regression", "failure-time prediction"],
    }


def simulation_scenarios() -> list[dict[str, Any]]:
    return [
        {"name": "network degradation", "variable": "latency", "range": "40-180ms", "expected_effect": "agency and ownership decline"},
        {"name": "sensor failure", "variable": "packet_loss", "range": "0-8%", "expected_effect": "reality sync drift"},
        {"name": "stress response", "variable": "workload", "range": "45-90", "expected_effect": "cognitive stability collapse"},
        {"name": "robot lag", "variable": "haptic_delay", "range": "20-220ms", "expected_effect": "control confidence loss"},
    ]


def neural_presence_state(metrics: dict[str, float]) -> dict[str, Any]:
    consciousness = embodied_consciousness(metrics)
    reality = reality_sync_state(metrics)
    emotional_bandwidth = max(0, min(100, 100 - abs(metrics.get("heart_rate", 82) - 88) * 1.3 - metrics.get("workload", 50) * 0.2))
    intention_clarity = max(0, min(100, metrics.get("agency", 65) * 0.7 + metrics.get("task_efficiency", 65) * 0.3))
    embodiment_signal = predict_embodiment_state(metrics)["predicted_embodiment_quality"]
    presence_transmission = round(statistics.mean([
        consciousness["presence_continuity"],
        reality["unified_reality_score"],
        emotional_bandwidth,
        intention_clarity,
        embodiment_signal,
    ]), 1)
    return {
        "presence_transmission": presence_transmission,
        "intention_clarity": round(intention_clarity, 1),
        "emotional_bandwidth": round(emotional_bandwidth, 1),
        "embodiment_signal": embodiment_signal,
        "state": "felt-present" if presence_transmission >= 75 else "partial-presence" if presence_transmission >= 55 else "presence-fragmented",
    }


def persistent_digital_self(participant_id: str, metrics: dict[str, float]) -> dict[str, Any]:
    twin = human_digital_twin(participant_id, metrics)
    memory = embodied_memory_graph(metrics)
    return {
        "identity": participant_id,
        "continuity_score": round(max(0, min(100, 70 + memory["memory_strength"] * 0.15 - twin["fatigue_index"] * 0.12)), 1),
        "embodiment_preferences": {
            "preferred_recovery": twin["embodiment_fingerprint"]["recovery_strategy"],
            "sensitivity": twin["embodiment_fingerprint"]["latency_sensitivity"],
            "stability_mode": "calm-focus" if twin["fatigue_index"] > 60 else "performance",
        },
        "memory_aware_summary": f"{participant_id} adapts as a {twin['adaptation_profile']} with {twin['embodiment_fingerprint']['recovery_strategy']} as the current recovery path.",
    }


def emotional_ai_companion(metrics: dict[str, float]) -> dict[str, Any]:
    cognitive = cognitive_state(metrics)
    forecast = failure_forecast(metrics)
    if cognitive["stress_escalation"] == "elevated":
        message = "Current inputs exceed the prototype workload threshold. Review workload-related measurements and settings before acting."
        tone = "supportive"
    elif forecast["rule_status"] == "elevated":
        message = "Current inputs activate an elevated deterministic rule condition. Review the flagged measurements before acting."
        tone = "directive"
    else:
        message = "Presence is holding. I will maintain sensory fidelity and monitor for drift."
        tone = "calm"
    return {
        "tone": tone,
        "message": message,
        "interventions": forecast["review_prompts"],
        "emotional_state_estimate": "overloaded" if cognitive["stress_escalation"] == "elevated" else "regulated",
    }


def sensory_presence_state(metrics: dict[str, float]) -> dict[str, Any]:
    haptic = max(0, min(100, 100 - max(0, metrics.get("haptic_delay", 30) - 40) * 0.35))
    visual = max(0, min(100, metrics.get("fps", 70) * 1.15))
    audio = max(0, min(100, 96 - metrics.get("packet_loss", 0) * 5))
    tactile = max(0, min(100, statistics.mean([haptic, metrics.get("ownership", 65)])))
    sensory_fidelity = round(statistics.mean([haptic, visual, audio, tactile]), 1)
    return {
        "haptic_fidelity": round(haptic, 1),
        "visual_fidelity": round(visual, 1),
        "spatial_audio_fidelity": round(audio, 1),
        "tactile_presence": round(tactile, 1),
        "full_sensory_presence": sensory_fidelity,
    }


def shared_reality_space(metrics: dict[str, float]) -> dict[str, Any]:
    trust = max(0, min(100, metrics.get("collaboration_quality", 70) * 0.7 + metrics.get("presence", 65) * 0.3))
    team_load = max(0, min(100, metrics.get("workload", 50) * 0.6 + max(0, metrics.get("latency", 50) - 70) * 0.2))
    synchrony = max(0, min(100, 100 - metrics.get("packet_loss", 0) * 4 - max(0, metrics.get("latency", 50) - 80) * 0.25))
    return {
        "collaboration_trust": round(trust, 1),
        "team_cognitive_load": round(team_load, 1),
        "social_presence_sync": round(synchrony, 1),
        "space_state": "co-present" if synchrony >= 75 and trust >= 70 else "loosely-coupled",
    }


def cognitive_augmentation(metrics: dict[str, float]) -> dict[str, Any]:
    mistake_risk = max(0, min(100, metrics.get("error_rate", 8) * 3 + max(0, metrics.get("workload", 50) - 65) * 1.2))
    focus_boost = max(0, min(100, 100 - cognitive_state(metrics)["attention_drift"]))
    precision_boost = max(0, min(100, metrics.get("agency", 65) * 0.4 + metrics.get("task_efficiency", 65) * 0.6))
    return {
        "mistake_prediction_risk": round(mistake_risk, 1),
        "focus_stabilization": round(focus_boost, 1),
        "control_precision_gain": round(precision_boost, 1),
        "augmentation_mode": "protective" if mistake_risk > 55 else "performance-amplifying",
    }


def reality_orchestration(metrics: dict[str, float]) -> dict[str, Any]:
    companion = emotional_ai_companion(metrics)
    sensory = sensory_presence_state(metrics)
    actions = list(companion["interventions"])
    if sensory["full_sensory_presence"] < 70:
        actions.append("rebalance sensory fidelity")
    if neural_presence_state(metrics)["presence_transmission"] < 60:
        actions.append("increase presence reinforcement")
    return {
        "orchestration_goal": "preserve embodiment continuity",
        "active_actions": actions,
        "environment_complexity": "reduced" if metrics.get("workload", 0) > 75 else "normal",
        "sensory_fidelity_target": "stabilize" if sensory["full_sensory_presence"] < 75 else "maximize",
    }


def post_screen_experience(metrics: dict[str, float], participant_id: str) -> dict[str, Any]:
    return {
        "neural_presence": neural_presence_state(metrics),
        "persistent_digital_self": persistent_digital_self(participant_id, metrics),
        "ai_companion": emotional_ai_companion(metrics),
        "sensory_presence": sensory_presence_state(metrics),
        "shared_reality": shared_reality_space(metrics),
        "cognitive_augmentation": cognitive_augmentation(metrics),
        "reality_orchestration": reality_orchestration(metrics),
    }


def _store_session(payload: ExperimentSession) -> StoredSession:
    session = StoredSession(
        id=len(SESSIONS) + 1,
        participant_id=payload.participant_id,
        task_type=payload.task_type,
        setup=payload.setup,
        session_time=payload.session_time or datetime.utcnow().isoformat(timespec="seconds"),
        metrics=payload.metrics,
    )
    session.scores = calculate_scores(session.metrics)
    session.insight = generate_insight(session)
    SESSIONS.append(session)
    return session


def _seed() -> None:
    if SESSIONS:
        return
    defaults = [
        ExperimentSession(
            participant_id="P-001",
            task_type="Remote object assembly",
            setup="VR headset + haptic glove",
            session_time="2026-05-22T09:15:00",
            metrics={
                "embodiment": 82,
                "ownership": 58,
                "agency": 88,
                "presence": 76,
                "task_efficiency": 81,
                "task_completion_time": 92,
                "error_rate": 6,
                "safety_events": 1,
                "workload": 62,
                "collaboration_quality": 78,
                "heart_rate": 94,
                "hrv": 51,
                "latency": 118,
                "fps": 72,
                "packet_loss": 2.1,
                "visual_match": 54,
                "haptic_delay": 140,
                "self_location": 72,
                "social_presence": 74,
                "situation_awareness": 69,
                "trust": 71,
                "path_efficiency": 79,
                "movement_smoothness": 68,
                "galvanic_response": 0.58,
                "cybersickness": 24,
                "usability": 76,
                "comfort": 70,
                "fatigue": 41,
                "jitter": 24,
                "tracking_dropout": 2,
                "calibration_error": 1.8,
                "timestamp_accuracy": 2.1,
                "missing_data_percent": 3.2,
                "fusion_latency": 48,
                "sampling_sync": 91,
                "visualization_clarity": 84,
                "explanation_satisfaction": 78,
                "autonomy_assistance": 44,
                "gaze_alignment": 82,
                "gesture_timing": 77,
                "conversational_latency": 168,
                "avatar_fidelity": 66,
                "adaptation_disclosed": 1,
                "override_available": 1,
            },
        ),
        ExperimentSession(
            participant_id="P-002",
            task_type="Remote navigation",
            setup="CAVE display + mobile robot",
            session_time="2026-05-22T10:00:00",
            metrics={
                "embodiment": 70,
                "ownership": 66,
                "agency": 73,
                "presence": 69,
                "task_efficiency": 74,
                "task_completion_time": 130,
                "error_rate": 11,
                "safety_events": 2,
                "workload": 76,
                "collaboration_quality": 64,
                "heart_rate": 106,
                "hrv": 42,
                "latency": 82,
                "fps": 61,
                "packet_loss": 1.3,
                "visual_match": 72,
                "haptic_delay": 58,
                "self_location": 65,
                "social_presence": 61,
                "situation_awareness": 58,
                "trust": 57,
                "path_efficiency": 64,
                "movement_smoothness": 60,
                "galvanic_response": 0.72,
                "cybersickness": 38,
                "usability": 68,
                "comfort": 57,
                "fatigue": 63,
                "jitter": 31,
                "tracking_dropout": 4,
                "calibration_error": 2.7,
                "timestamp_accuracy": 3.4,
                "missing_data_percent": 5.8,
                "fusion_latency": 76,
                "sampling_sync": 82,
                "visualization_clarity": 74,
                "explanation_satisfaction": 62,
                "autonomy_assistance": 72,
                "gaze_alignment": 67,
                "gesture_timing": 62,
                "conversational_latency": 244,
                "avatar_fidelity": 78,
                "adaptation_disclosed": 0,
                "override_available": 1,
            },
        ),
    ]
    for item in defaults:
        _store_session(item)


def _session_response(session: StoredSession) -> dict[str, Any]:
    return {
        "software_version": SOFTWARE_VERSION,
        "api_schema_version": API_SCHEMA_VERSION,
        "id": session.id,
        "participant_id": session.participant_id,
        "task_type": session.task_type,
        "setup": session.setup,
        "session_time": session.session_time,
        "metrics": session.metrics,
        "scores": session.scores,
        "insight": session.insight,
        "risk_events": detect_risks(session.metrics),
        "embodiment_prediction": predict_embodiment_state(session.metrics),
        "cognitive_state": cognitive_state(session.metrics),
        "prediction_explanation": explain_prediction(session.metrics),
        "failure_forecast": failure_forecast(session.metrics),
        "embodied_consciousness": embodied_consciousness(session.metrics),
        "human_digital_twin": human_digital_twin(session.participant_id, session.metrics),
        "embodied_memory_graph": embodied_memory_graph(session.metrics),
        "tlm_interpretation": telepresence_language_model(session.metrics),
        "reality_sync": reality_sync_state(session.metrics),
        "autonomous_scientist": autonomous_scientist(session.metrics),
        "post_screen_experience": post_screen_experience(session.metrics, session.participant_id),
        "catem": catem_assessment(session.metrics),
        "measurement_records": measurement_contract(
            session.metrics,
            timestamp=session.session_time,
            source="stored_session",
        ),
    }


def _pearson(x_values: list[float], y_values: list[float]) -> float | None:
    if len(x_values) < 2 or len(x_values) != len(y_values):
        return None
    x_mean = statistics.mean(x_values)
    y_mean = statistics.mean(y_values)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, y_values))
    x_variance = sum((x - x_mean) ** 2 for x in x_values)
    y_variance = sum((y - y_mean) ** 2 for y in y_values)
    denominator = math.sqrt(x_variance * y_variance)
    if denominator == 0:
        return None
    return round(numerator / denominator, 3)


def _correlation_pair(x_key: str, y_key: str) -> dict[str, Any]:
    pairs = [
        (session.metrics[x_key], session.metrics[y_key])
        for session in SESSIONS
        if x_key in session.metrics and y_key in session.metrics
    ]
    if len(pairs) < 3:
        return {
            "x": x_key,
            "y": y_key,
            "pearson_r": None,
            "n": len(pairs),
            "status": "insufficient_sample",
        }
    x_values, y_values = zip(*pairs)
    return {
        "x": x_key,
        "y": y_key,
        "pearson_r": _pearson(list(x_values), list(y_values)),
        "n": len(pairs),
        "status": "descriptive_only",
    }


def _analytics() -> dict[str, Any]:
    if not SESSIONS:
        return {"relationships": [], "averages": {}}

    averages: dict[str, float] = {}
    all_keys = sorted({key for session in SESSIONS for key in session.metrics})
    for key in all_keys:
        values = [session.metrics[key] for session in SESSIONS if key in session.metrics]
        averages[key] = round(statistics.mean(values), 2)

    relationships = [
        {
            "label": "Candidate pattern: higher latency co-occurs with lower agency in current fixtures",
            "status": "observed" if averages.get("latency", 0) > 90 and averages.get("agency", 100) < 80 else "monitor",
        },
        {
            "label": "Candidate descriptive pattern: higher embodiment and task performance co-vary in current fixtures",
            "status": "descriptive pattern"
            if averages.get("embodiment", 0) >= 70 and averages.get("task_efficiency", 0) >= 70
            else "monitor",
        },
        {
            "label": "Candidate descriptive pattern: higher workload co-occurs with more errors in current fixtures",
            "status": "descriptive pattern" if averages.get("workload", 0) > 65 and averages.get("error_rate", 0) > 8 else "monitor",
        },
    ]
    correlations = [
        _correlation_pair("latency", "agency"),
        _correlation_pair("embodiment", "task_efficiency"),
        _correlation_pair("workload", "error_rate"),
        _correlation_pair("heart_rate", "error_rate"),
    ]
    risk_counts: dict[str, int] = {}
    for session in SESSIONS:
        for risk in detect_risks(session.metrics):
            risk_counts[risk["type"]] = risk_counts.get(risk["type"], 0) + 1

    return {
        "relationships": relationships,
        "averages": averages,
        "correlations": correlations,
        "risk_counts": risk_counts,
    }


@router.get("/metrics")
def get_metrics() -> dict[str, Any]:
    _seed()
    latest = SESSIONS[-1]
    return {
        "latest": _session_response(latest),
        "sessions": [_session_response(session) for session in SESSIONS],
        "analytics": _analytics(),
    }


@router.post("/sessions")
def create_session(payload: ExperimentSession) -> dict[str, Any]:
    return _session_response(_store_session(payload))


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)) -> dict[str, Any]:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    content = (await file.read()).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(content))
    created: list[dict[str, Any]] = []
    for row in reader:
        participant_id = row.get("participant_id") or row.get("participant") or row.get("id")
        if not participant_id:
            continue
        metrics = {
            key: number
            for key, value in row.items()
            if key
            not in {
                "participant_id",
                "participant",
                "id",
                "task_type",
                "setup",
                "session_time",
            }
            and (number := _numeric(value)) is not None
        }
        created.append(
            _session_response(
                _store_session(
                    ExperimentSession(
                        participant_id=participant_id,
                        task_type=row.get("task_type") or "Uploaded session",
                        setup=row.get("setup") or "Telepresence setup",
                        session_time=row.get("session_time") or None,
                        metrics=metrics,
                    )
                )
            )
        )

    if not created:
        raise HTTPException(status_code=400, detail="No valid participant rows were found.")
    return {"created": created, "count": len(created), "analytics": _analytics()}


@router.get("/analysis")
def analysis() -> dict[str, Any]:
    _seed()
    return _analytics()


@router.get("/platform/architecture")
def platform_architecture() -> dict[str, Any]:
    return {
        "name": "Embodied AI Research Operating Platform",
        "software_version": SOFTWARE_VERSION,
        "catem_version": CATEM_VERSION,
        "api_schema_version": API_SCHEMA_VERSION,
        "runtime": {
            "python": platform.python_version(),
            "implementation": platform.python_implementation(),
            "operating_system": platform.system(),
        },
        "storage": {
            "mode": "in_memory_prototype",
            "durable": False,
        },
        "security_assumptions": [
            "local trusted research network",
            "no authentication or authorization in the prototype",
            "no sensitive human-subject data without an approved deployment layer",
        ],
        "pipeline": [
            "human operator",
            "VR/AR/robot interface",
            "multimodal sensor fusion layer",
            "real-time cognitive state engine",
            "embodiment intelligence model",
            "adaptive telepresence system",
            "research analytics and AI copilot",
        ],
        "stream_sources": [
            "telemetry simulator",
            "EEG",
            "HRV",
            "eye tracking",
            "hand tracking",
            "motion tracking",
            "robot telemetry",
            "network latency",
            "video/audio streams",
        ],
        "research_modules": [
            "cognitive state engine",
            "embodied AI relationship graph",
            "spatial 3D research environment",
            "autonomous AI research agent",
            "digital human model",
            "live research timeline",
            "embodied consciousness layer",
            "human digital twin",
            "telepresence language model",
            "reality synchronization engine",
            "embodied memory graph",
            "scientific simulation engine",
            "neural presence system",
            "persistent digital self",
            "emotionally intelligent AI companion",
            "full-sensory telepresence",
            "shared reality spaces",
            "cognitive augmentation layer",
            "autonomous reality orchestration",
            "explainable AI layer",
            "predictive failure engine",
            "adaptive optimization loop",
            "dynamic embodiment graph",
            "risk detection",
            "digital twin replay",
            "correlation engine",
            "predictive modeling",
            "AI research assistant",
            "dataset builder",
        ],
        "simulator": SIMULATOR.profile(),
    }


@router.post("/telemetry")
def ingest_telemetry(event: TelemetryEvent) -> dict[str, Any]:
    payload = event.dict()
    payload["timestamp"] = payload["timestamp"] or datetime.utcnow().isoformat(timespec="milliseconds")
    payload["software_version"] = SOFTWARE_VERSION
    payload["api_schema_version"] = API_SCHEMA_VERSION
    payload["risk_events"] = detect_risks(payload["metrics"])
    payload["embodiment_prediction"] = predict_embodiment_state(payload["metrics"])
    payload["cognitive_state"] = cognitive_state(payload["metrics"])
    payload["prediction_explanation"] = explain_prediction(payload["metrics"])
    payload["failure_forecast"] = failure_forecast(payload["metrics"])
    payload["embodied_consciousness"] = embodied_consciousness(payload["metrics"])
    payload["human_digital_twin"] = human_digital_twin(payload["participant_id"], payload["metrics"])
    payload["embodied_memory_graph"] = embodied_memory_graph(payload["metrics"])
    payload["tlm_interpretation"] = telepresence_language_model(payload["metrics"])
    payload["reality_sync"] = reality_sync_state(payload["metrics"])
    payload["autonomous_scientist"] = autonomous_scientist(payload["metrics"])
    payload["post_screen_experience"] = post_screen_experience(payload["metrics"], payload["participant_id"])
    payload["catem"] = catem_assessment(payload["metrics"])
    payload["measurement_records"] = measurement_contract(
        payload["metrics"],
        timestamp=payload["timestamp"],
        source=payload["source"],
    )
    TELEMETRY_STREAM.append(payload)
    return payload


@router.get("/telemetry/latest")
def latest_telemetry() -> dict[str, Any]:
    return {"events": TELEMETRY_STREAM[-50:]}


@router.get("/research/scientist")
def research_scientist() -> dict[str, Any]:
    _seed()
    latest = SESSIONS[-1]
    return autonomous_scientist(latest.metrics)


@router.get("/events/object-drop")
def object_drop_event() -> dict[str, Any]:
    return object_drop_event_window()


@router.get("/simulation/scenarios")
def simulation_catalog() -> dict[str, Any]:
    return {"scenarios": simulation_scenarios()}


@router.get("/simulation/telemetry-profile")
def telemetry_simulator_profile() -> dict[str, Any]:
    return SIMULATOR.profile()


@router.get("/simulation/telemetry-preview")
def telemetry_simulator_preview() -> dict[str, Any]:
    _seed()
    frames = []
    for tick in range(16):
        session = SESSIONS[tick % len(SESSIONS)]
        metrics, simulator_state = SIMULATOR.simulate(session.metrics, tick)
        frames.append(
            {
                "tick": tick,
                "participant_id": session.participant_id,
                "phase": simulator_state["phase"],
                "metrics": metrics,
                "simulator_state": simulator_state,
            }
        )
    return {"profile": SIMULATOR.profile(), "frames": frames}


@router.get("/presence/post-screen")
def post_screen_presence() -> dict[str, Any]:
    _seed()
    latest = SESSIONS[-1]
    return post_screen_experience(latest.metrics, latest.participant_id)


@router.websocket("/ws/telemetry")
async def telemetry_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    _seed()
    tick = 0
    try:
        while True:
            session = SESSIONS[tick % len(SESSIONS)]
            simulated, simulator_state = SIMULATOR.simulate(session.metrics, tick)
            event = {
                "software_version": SOFTWARE_VERSION,
                "api_schema_version": API_SCHEMA_VERSION,
                "timestamp": datetime.utcnow().isoformat(timespec="milliseconds"),
                "participant_id": session.participant_id,
                "source": "real_telemetry_simulator",
                "metrics": simulated,
                "simulator_state": simulator_state,
                "risk_events": detect_risks(simulated),
                "embodiment_prediction": predict_embodiment_state(simulated),
                "cognitive_state": cognitive_state(simulated),
                "prediction_explanation": explain_prediction(simulated),
                "failure_forecast": failure_forecast(simulated),
                "embodied_consciousness": embodied_consciousness(simulated),
                "human_digital_twin": human_digital_twin(session.participant_id, simulated),
                "embodied_memory_graph": embodied_memory_graph(simulated),
                "tlm_interpretation": telepresence_language_model(simulated),
                "reality_sync": reality_sync_state(simulated),
                "autonomous_scientist": autonomous_scientist(simulated),
                "post_screen_experience": post_screen_experience(simulated, session.participant_id),
                "catem": catem_assessment(simulated),
            }
            event["measurement_records"] = measurement_contract(
                simulated,
                timestamp=event["timestamp"],
                source=event["source"],
            )
            TELEMETRY_STREAM.append(event)
            await websocket.send_json(event)
            tick += 1
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
