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
- AI-style performance summaries
- Telepresence scoring system
- Real-time telemetry WebSocket stream
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
- AI-SBOM reliability monitoring
- Intelligent risk detection
- Pearson correlation analytics
- Research platform architecture endpoint

## CSV Format
Use the sample in `data/sample_metrics.csv` or upload rows with these columns:

```text
participant_id,task_type,setup,session_time,embodiment,ownership,agency,presence,task_efficiency,task_completion_time,error_rate,safety_events,workload,collaboration_quality,heart_rate,hrv,latency,fps,packet_loss,visual_match,haptic_delay
```

## Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8010
```

## Run Frontend
```bash
cd frontend
npm install
npm run dev
```

Open the frontend at `http://127.0.0.1:5180`. In this workspace the frontend `.env.local` points to `http://127.0.0.1:8010` because port 8000 is already occupied.

## V1 Execution Docs
- `docs/V1_EXECUTION_PLAN.md`
- `docs/AI_PIPELINE.md`
- `docs/DATA_STRATEGY.md`
- `docs/DEPLOYMENT_ARCHITECTURE.md`
- `docs/RESEARCH_ROADMAP.md`

## Target Architecture
```text
apps/
  web/
  api/
  ai-engine/

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
- `GET /analysis` returns averages, relationships, correlations, and risk counts.

See `docs/advanced_platform.md` for the PhD/research-grade architecture and ultimate research vision.
