# Telemetry Service

Responsibilities:
- WebSocket telemetry stream.
- CSV ingestion.
- Replay buffer.
- Time-window aggregation.
- Modality quality flags.
- Realistic telemetry simulation for hardware-free research demos.

V1 simulation lives in `services/telemetry/simulator.py` and is consumed by the FastAPI WebSocket route.

## Real Telemetry Simulator

The simulator is split into four generators:

- Physiological simulator: heart rate, HRV, respiration, galvanic response.
- Network simulator: latency, jitter, packet loss, FPS, bandwidth, compression level.
- Embodiment degradation simulator: agency, ownership, presence, visual match, haptic delay, gaze stability, motion entropy.
- Stress escalation simulator: workload, stress index, error rate, timing variance, safety events.

The WebSocket stream cycles through baseline alignment, network degradation, stress escalation, and adaptive recovery. This makes the platform feel alive without needing VR hardware, robot telemetry, or physiological sensors during early development.
