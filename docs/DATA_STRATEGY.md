# Data Strategy

## Multimodal Dataset
The long-term moat is a synchronized multimodal dataset for embodiment, cognition, and adaptive telepresence.

## V1 Data Sources
- CSV experiment uploads.
- WebSocket telemetry.
- Session metrics.
- System logs.
- Questionnaire scores.

## Target Data Sources
- HRV.
- EEG.
- gaze direction and fixation duration.
- hand tracking.
- motion entropy.
- interaction timing.
- robot telemetry.
- latency, FPS, packet loss.
- haptic delay.
- embodiment surveys.

## Label Strategy
Labels should support both research and model training:
- agency.
- ownership.
- presence.
- cognitive overload.
- fatigue.
- immersion collapse.
- teleoperation instability.
- recovery success.

## Synchronization Strategy
Every event should carry:
- `session_id`
- `participant_id`
- `source`
- `timestamp`
- `modality`
- `metrics`
- `quality_flags`

## Dataset Export
Future export formats:
- CSV for statistical analysis.
- JSONL for sequence modeling.
- Parquet for scalable analytics.
- vector documents for RAG.

## Research Advantage
The dataset should become the platform advantage: each session improves the digital twin, embodiment model, cognitive stability model, and adaptive reality policy.
