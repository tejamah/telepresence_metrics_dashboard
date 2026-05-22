from __future__ import annotations

import csv
import io
import statistics
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from fastapi import APIRouter, File, HTTPException, UploadFile
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
    return {"relationships": relationships, "averages": averages}


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
