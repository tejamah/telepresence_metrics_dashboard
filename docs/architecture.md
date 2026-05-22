
# System Architecture

## MVP Flow
1. Researchers upload CSV rows from questionnaires, sensor logs, or experiment sheets.
2. The FastAPI backend normalizes submetrics into category scores.
3. The analytics layer compares latency, embodiment, workload, errors, and performance.
4. The React dashboard shows the latest session, participant comparisons, and AI-style summaries.
5. PostgreSQL tables in `database/schema.sql` describe the production persistence model.

## Advanced Flow
1. Human operators interact through VR, AR, robot, WebXR, Unity, Unreal, OpenXR, or Meta Quest interfaces.
2. A multimodal sensor fusion layer synchronizes EEG, HRV, gaze, hand tracking, motion traces, robot telemetry, network metrics, and WebRTC quality.
3. A real-time cognitive state engine estimates overload, attention drift, stress escalation, and immersion collapse risk.
4. An embodiment intelligence model tracks agency, ownership, presence, latency, stress, and performance as a dynamic relationship graph.
5. An embodied AI consciousness layer models awareness, attention, control confidence, adaptation, and presence continuity.
6. A human digital twin stores physiological baselines, adaptation profiles, embodiment fingerprints, and recovery memories.
7. A telepresence language model translates telemetry into predictions, explanations, and adaptive decisions.
8. A reality synchronization engine aligns robot state, VR state, physiological streams, digital twin state, and AI predictions.
9. A predictive failure engine forecasts teleoperation instability before unsafe breakdowns occur.
10. An AI-SBOM reliability monitor links dependency instability to embodiment degradation and teleoperation failures.
11. An adaptive telepresence loop tunes graphics quality, haptic intensity, compression, and robot responsiveness.
12. The autonomous HRI scientist generates hypotheses, suggested experiments, explanations, and paper-ready findings.

## Post-Screen Presence Flow
1. Neural presence models intention clarity, emotional bandwidth, cognitive state, and embodiment signal.
2. Persistent digital self profiles preserve operator identity, memory, preferences, recovery strategies, and behavioral continuity.
3. Emotionally intelligent AI companion interventions support the operator when overload, drift, or instability emerges.
4. Full-sensory telepresence models haptic, visual, spatial audio, and tactile fidelity.
5. Shared reality spaces estimate collaboration trust, team cognitive load, and social presence synchronization.
6. Autonomous reality orchestration adapts sensory fidelity, environmental complexity, compression, and teleoperation behavior to preserve presence continuity.

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
