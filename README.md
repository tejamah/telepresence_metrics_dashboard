
# Telepresence Metrics Dashboard

## Overview
This project is designed for Human-Robot Interaction (HRI), Telepresence, and VR research.
It collects, analyzes, and visualizes embodiment, presence, performance, behavioral,
physiological, and system metrics.

## Tech Stack
- Frontend: React
- Backend: FastAPI
- Database: PostgreSQL
- Visualization: Chart.js
- AI Analysis: Future integration with LLMs

## Features
- Metrics collection
- CSV upload
- Dashboard scorecards and comparison tables
- AI-style performance summaries
- Telepresence scoring system

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
