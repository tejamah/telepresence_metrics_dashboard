from __future__ import annotations

import asyncio
import csv
import io
import math
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

router = APIRouter()


METRIC_WEIGHTS = {
    "embodiment": 0.2,
    "presence": 0.18,
    "performance": 0.18,
    "behavior": 0.12,
    "physiological": 0.12,
    "system": 0.14,
    "visualization": 0.06,
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
    if name == "task_completion_time":
        return _score_negative(value, 45, 240)
    if name == "error_rate":
        return _score_negative(value, 2, 25)
    if name == "safety_events":
        return _score_negative(value, 0, 6)
    if name == "heart_rate":
        return _score_negative(value, 70, 120)
    if name == "latency":
        return _score_negative(value, 30, 180)
    if name == "packet_loss":
        return _score_negative(value, 0.5, 8)
    if name == "haptic_delay":
        return _score_negative(value, 20, 220)
    if name == "fps":
        return min(100, max(20, (value / 90) * 100))
    return _score_positive(value)


def _grade(score: float) -> str:
    if score >= 75:
        return "high"
    if score >= 50:
        return "medium"
    return "low"


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


def generate_insight(session: StoredSession) -> str:
    metrics = session.metrics
    scores = session.scores["categories"]
    clauses: list[str] = []

    if metrics.get("agency", 0) >= 75 and metrics.get("ownership", 100) < 60:
        clauses.append("strong agency but reduced ownership, likely from visual mismatch or delayed feedback")
    if metrics.get("latency", 0) > 100:
        clauses.append("high latency may be suppressing presence and agency")
    if metrics.get("workload", 0) > 70 and metrics.get("error_rate", 0) > 10:
        clauses.append("high workload is paired with elevated error rates")
    if scores["embodiment"]["score"] >= 75 and scores["performance"]["score"] >= 70:
        clauses.append("embodiment appears to support task performance")
    if metrics.get("heart_rate", 0) > 110 or metrics.get("hrv", 100) < 40:
        clauses.append("physiological signals suggest stress or fatigue")
    if not clauses:
        clauses.append("the session shows balanced telepresence quality with no dominant risk signal")

    return f"Participant {session.participant_id} showed {', and '.join(clauses)}."


def detect_risks(metrics: dict[str, float]) -> list[dict[str, Any]]:
    rules = [
        ("unstable sensor pipeline", metrics.get("packet_loss", 0) > 5, "high packet loss can desynchronize multimodal streams"),
        ("synchronization failure", metrics.get("latency", 0) > 150, "network or rendering delay exceeds teleoperation comfort bounds"),
        ("embodiment degradation", metrics.get("agency", 100) < 55 or metrics.get("ownership", 100) < 55, "agency or ownership has dropped below research threshold"),
        ("cognitive overload", metrics.get("workload", 0) > 80 or metrics.get("heart_rate", 0) > 115, "workload and physiology suggest stress"),
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
            },
        ),
    ]
    for item in defaults:
        _store_session(item)


def _session_response(session: StoredSession) -> dict[str, Any]:
    return {
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
    if not pairs:
        return {"x": x_key, "y": y_key, "pearson_r": None, "n": 0}
    x_values, y_values = zip(*pairs)
    return {
        "x": x_key,
        "y": y_key,
        "pearson_r": _pearson(list(x_values), list(y_values)),
        "n": len(pairs),
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
            "label": "Higher latency -> lower agency",
            "status": "observed" if averages.get("latency", 0) > 90 and averages.get("agency", 100) < 80 else "monitor",
        },
        {
            "label": "Higher embodiment -> better task performance",
            "status": "observed"
            if averages.get("embodiment", 0) >= 70 and averages.get("task_efficiency", 0) >= 70
            else "monitor",
        },
        {
            "label": "Higher workload -> more errors",
            "status": "observed" if averages.get("workload", 0) > 65 and averages.get("error_rate", 0) > 8 else "monitor",
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
        "name": "Intelligent Multimodal Telepresence Analytics Platform",
        "pipeline": [
            "VR/robot devices",
            "sensor streaming layer",
            "real-time processing engine",
            "AI analytics engine",
            "embodiment and presence scoring",
            "research dashboard and reports",
        ],
        "stream_sources": [
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
            "dynamic embodiment graph",
            "risk detection",
            "digital twin replay",
            "correlation engine",
            "predictive modeling",
            "AI research assistant",
            "dataset builder",
        ],
    }


@router.post("/telemetry")
def ingest_telemetry(event: TelemetryEvent) -> dict[str, Any]:
    payload = event.dict()
    payload["timestamp"] = payload["timestamp"] or datetime.utcnow().isoformat(timespec="milliseconds")
    payload["risk_events"] = detect_risks(payload["metrics"])
    payload["embodiment_prediction"] = predict_embodiment_state(payload["metrics"])
    TELEMETRY_STREAM.append(payload)
    return payload


@router.get("/telemetry/latest")
def latest_telemetry() -> dict[str, Any]:
    return {"events": TELEMETRY_STREAM[-50:]}


@router.websocket("/ws/telemetry")
async def telemetry_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    _seed()
    tick = 0
    try:
        while True:
            base = SESSIONS[tick % len(SESSIONS)].metrics
            simulated = {
                **base,
                "latency": round(base.get("latency", 80) + math.sin(tick / 3) * 18, 2),
                "packet_loss": round(max(0, base.get("packet_loss", 1) + math.cos(tick / 4) * 0.7), 2),
                "heart_rate": round(base.get("heart_rate", 90) + math.sin(tick / 2) * 5, 2),
                "agency": round(max(0, min(100, base.get("agency", 70) - max(0, math.sin(tick / 3) * 8))), 2),
            }
            event = {
                "timestamp": datetime.utcnow().isoformat(timespec="milliseconds"),
                "participant_id": SESSIONS[tick % len(SESSIONS)].participant_id,
                "source": "websocket_simulator",
                "metrics": simulated,
                "risk_events": detect_risks(simulated),
                "embodiment_prediction": predict_embodiment_state(simulated),
            }
            TELEMETRY_STREAM.append(event)
            await websocket.send_json(event)
            tick += 1
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
