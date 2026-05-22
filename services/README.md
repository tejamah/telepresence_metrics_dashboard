# Services

Service boundaries for the V1 platform.

```text
services/
  telemetry/        live ingestion, WebSocket streaming, replay buffers
  cognition/        cognitive stability, overload, fatigue, stress escalation
  embodiment/       agency, ownership, presence, embodiment collapse prediction
  synchronization/  reality sync, timestamp alignment, sensor fusion
  ai-copilot/       insights, explanations, research assistant, AI companion
```

Each service should expose pure domain logic first, then worker/API adapters later. This keeps research models testable without requiring Kafka, Redis, or production infrastructure during the MVP.
