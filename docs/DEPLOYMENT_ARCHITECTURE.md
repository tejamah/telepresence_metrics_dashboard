# Deployment Architecture

## Local V1

```text
Browser
  -> React TypeScript app
  -> FastAPI REST + WebSocket API
  -> in-memory session store
  -> PostgreSQL schema ready
```

## Production V1 Target

```text
Browser / VR Client
  -> Web app CDN
  -> API gateway
  -> FastAPI API service
  -> WebSocket telemetry service
  -> PostgreSQL
  -> Redis replay buffer
  -> AI worker service
```

## Future Production Target

```text
VR / AR / Robot Interfaces
  -> Kafka telemetry topics
  -> Stream processors
  -> Cognition + Embodiment services
  -> AI copilot / RAG service
  -> TimescaleDB + PostgreSQL + Vector DB
  -> Research dashboard + SDKs
```

## Environment Variables
- `VITE_API_URL`: frontend API base URL.
- `DATABASE_URL`: PostgreSQL connection string.
- `REDIS_URL`: replay buffer and task queue.
- `MODEL_REGISTRY_URL`: future model registry.
- `VECTOR_DB_URL`: future RAG and research memory store.

## Deployment Milestones
1. Single-machine demo with FastAPI and static frontend.
2. Docker Compose with web, api, and PostgreSQL.
3. Managed deployment with persistent database.
4. Streaming deployment with Redis/Kafka.
5. Research cloud deployment with AI workers and vector database.
