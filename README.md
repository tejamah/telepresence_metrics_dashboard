
# Intelligent Multimodal Telepresence Analytics Platform

## Overview
This project is designed for Human-Robot Interaction (HRI), Telepresence, VR, and robotics research.
It is evolving from a metrics dashboard into a real-time multimodal analytics platform for embodiment,
presence, behavioral, physiological, system, and risk evaluation.

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

See `docs/advanced_platform.md` for the PhD/research-grade architecture.
