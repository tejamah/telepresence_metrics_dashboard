
# Embodied AI Research Operating Platform

## Overview
This project is designed for Human-Robot Interaction (HRI), telepresence, VR/AR, robotics, and embodied AI research.
It is evolving from a metrics dashboard into a real-time research operating platform for cognitive state estimation,
embodiment intelligence, adaptive telepresence, AI-SBOM reliability, and publishable multimodal analytics.

## Tech Stack
- Frontend: React, future TypeScript/Tailwind/D3/Three.js modules
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

## Research Platform Endpoints
- `GET /platform/architecture` returns the advanced platform pipeline.
- `POST /telemetry` ingests multimodal sensor telemetry.
- `GET /telemetry/latest` returns recent telemetry events.
- `WS /ws/telemetry` streams simulated real-time telemetry for development.
- `GET /analysis` returns averages, relationships, correlations, and risk counts.

See `docs/advanced_platform.md` for the PhD/research-grade architecture and ultimate research vision.
