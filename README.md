# Embodied Presence Internet

## Overview
This project is designed for Human-Robot Interaction (HRI), telepresence, VR/AR, robotics, and embodied AI research.
It is evolving from a metrics dashboard into post-screen human experience infrastructure for remote presence,
persistent digital identity, cognitive augmentation, emotionally intelligent AI companionship, adaptive reality,
and publishable multimodal analytics.

## Tech Stack
- Frontend: React + TypeScript, Tailwind-ready design system, future Framer Motion/Recharts/Three.js modules
- Backend: FastAPI, WebSockets
- Data Layer: PostgreSQL schema with TimescaleDB/vector DB expansion points
- Streaming Target: Kafka, Redis, Celery workers, Spark Streaming
- AI Target: PyTorch, HuggingFace Transformers, LangChain/RAG, LLM insight generation

## Features
- Metrics collection
- CSV upload
- Dashboard scorecards and comparison tables
- Traceable five-sample object-drop event window
- AI-style performance summaries
- Telepresence scoring system
- Real telemetry simulator for hardware-free live demos
- Real-time telemetry WebSocket stream with simulator state
- Embodiment prediction
- Cognitive state engine
- Embodied AI consciousness layer
- Human digital twin
- Telepresence language model interpretation
- Reality synchronization engine
- Embodied memory graph
- Autonomous HRI scientist
- Neural presence system
- Persistent digital self
- Emotionally intelligent AI companion
- Full-sensory telepresence model
- Shared reality space model
- Autonomous reality orchestration
- Predictive failure engine
- Explainable AI factors
- Intelligent risk detection
- Pearson correlation analytics
- Research platform architecture endpoint

## CSV Format
Use the sample in `data/sample_metrics.csv` or upload rows with these columns:

```text
participant_id,task_type,setup,session_time,embodiment,ownership,agency,self_location,presence,social_presence,situation_awareness,trust,task_efficiency,task_completion_time,error_rate,path_efficiency,safety_events,workload,collaboration_quality,heart_rate,hrv,galvanic_response,cybersickness,latency,jitter,fps,packet_loss,tracking_dropout,visual_match,haptic_delay,timestamp_accuracy,missing_data_percent,fusion_latency,sampling_sync,autonomy_assistance,adaptation_disclosed,override_available
```

## Run Backend
```bash
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8010
```

## Run Frontend
```bash
cd apps/web
npm install
npm run dev
```

Open the web app at `http://127.0.0.1:5180`. The web app defaults to `http://127.0.0.1:8010` for the API.

## V1 Execution Docs
- `docs/V1_EXECUTION_PLAN.md`
- `docs/AI_PIPELINE.md`
- `docs/DATA_STRATEGY.md`
- `docs/DEPLOYMENT_ARCHITECTURE.md`
- `docs/RESEARCH_ROADMAP.md`

## Target Architecture
```text
apps/
  web/        React + TypeScript experience layer
  api/        FastAPI REST/WebSocket platform API
  ai-engine/  model training, evaluation, and future inference

services/
  telemetry/
  cognition/
  embodiment/
  synchronization/
  ai-copilot/

packages/
  ui/
  types/
  analytics/
```

## Research Platform Endpoints
- `GET /platform/architecture` returns the advanced platform pipeline.
- `POST /telemetry` ingests multimodal sensor telemetry.
- `GET /telemetry/latest` returns recent telemetry events.
- `WS /ws/telemetry` streams simulated real-time telemetry for development.
- `GET /simulation/telemetry-profile` returns simulator phases and signal generators.
- `GET /simulation/telemetry-preview` returns a short generated telemetry sequence.
- `GET /analysis` returns averages, relationships, correlations, and risk counts.
- `GET /events/object-drop` returns the canonical (reference) event fixture: five samples at
  offsets `-2`, `-1`, `0`, `+1`, and `+2` seconds, 35 traceable source records, and the
  software, CATEM, and API-schema versions used to produce them.

See `docs/advanced_platform.md` for the PhD/research-grade architecture and ultimate research vision.
See `docs/TELEMETRY_SIMULATOR.md` for the physiological, network, embodiment degradation, and stress escalation simulator.

## CATEM Reproducibility

Reviewer-facing CATEM materials are indexed in
[`docs/CATEM_REPRODUCIBILITY.md`](docs/CATEM_REPRODUCIBILITY.md). The index
links directly to the dashboard screenshot, sample CSV, canonical event fixture,
measurement and response schemas, verification results, and exact run commands.

## License and Citation

This project is open source under the [MIT License](LICENSE). Machine-readable
citation metadata for CATEM version 0.2.0 are provided in [CITATION.cff](CITATION.cff).
