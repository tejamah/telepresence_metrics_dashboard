
# System Architecture

## MVP Flow
1. Researchers upload CSV rows from questionnaires, sensor logs, or experiment sheets.
2. The FastAPI backend normalizes submetrics into category scores.
3. The analytics layer compares latency, embodiment, workload, errors, and performance.
4. The React dashboard shows the latest session, participant comparisons, and AI-style summaries.
5. PostgreSQL tables in `database/schema.sql` describe the production persistence model.

## Advanced Flow
1. ROS2, Unity, Unreal, OpenXR, and Meta Quest adapters publish synchronized device telemetry.
2. Kafka topics separate EEG, HRV, eye tracking, hand tracking, robot telemetry, network metrics, and WebRTC quality signals.
3. A real-time processing layer computes windowed aggregates, missing-sensor alerts, jitter, latency, and alignment quality.
4. AI models predict embodiment quality, cognitive overload, motion-sickness risk, and teleoperation failure.
5. A risk engine flags unsafe control conditions, hallucinated robot state, sensor instability, and embodiment degradation.
6. The dashboard renders live telemetry, dynamic embodiment graphs, replayable digital twin state, and paper-ready reports.

## API
- `GET /metrics` returns seeded or uploaded sessions, scores, insights, and aggregate relationships.
- `POST /upload-csv` accepts CSV files with `participant_id`, `task_type`, `setup`, `session_time`, and metric columns.
- `POST /sessions` accepts one JSON session with a `metrics` object.
- `GET /analysis` returns aggregate metric averages and relationship labels.
- `GET /platform/architecture` returns the advanced research platform pipeline.
- `POST /telemetry` ingests live or replayed multimodal telemetry.
- `GET /telemetry/latest` returns recent stream events.
- `WS /ws/telemetry` streams simulated real-time telemetry.

## Metric Categories
- Embodiment: embodiment, ownership, agency.
- Presence: subjective presence score.
- Performance: task efficiency, completion time, error rate.
- Behavioral: safety events, workload, collaboration quality.
- Physiological: heart rate and HRV.
- System: latency, FPS, packet loss, haptic delay.
- Visualization: visual match between avatar, robot, or environment and expected feedback.

## CSV Columns
Recommended columns:

```text
participant_id,task_type,setup,session_time,embodiment,ownership,agency,presence,task_efficiency,task_completion_time,error_rate,safety_events,workload,collaboration_quality,heart_rate,hrv,latency,fps,packet_loss,visual_match,haptic_delay
```

Higher values are better for embodiment, ownership, agency, presence, task efficiency, collaboration quality, HRV, FPS, and visual match. Lower values are better for completion time, error rate, safety events, workload, heart rate, latency, packet loss, and haptic delay.
