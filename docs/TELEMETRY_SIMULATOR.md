# Real Telemetry Simulator

The V1 platform now includes a hardware-free telemetry simulator that creates believable live multimodal signals for demos, testing, and early research workflows.

## Purpose

The simulator lets the system behave like a real embodied telepresence lab before expensive hardware is connected. It drives the WebSocket stream with coordinated changes across physiology, network quality, embodiment, and stress.

## Simulated Subsystems

- Physiological simulator: heart rate, HRV, respiration rate, galvanic response.
- Network simulator: latency, jitter, packet loss, FPS, bandwidth, compression level.
- Embodiment degradation simulator: agency, ownership, presence, visual match, haptic delay, gaze stability, motion entropy.
- Stress escalation simulator: workload, stress index, error rate, interaction timing variance, safety events.

## Runtime Phases

The simulator uses a 48-second cycle:

- `baseline_alignment`: stable physiology and moderate network load.
- `network_degradation`: latency, jitter, and packet loss rise.
- `stress_escalation`: physiological stress, workload, errors, and safety risk rise.
- `rule_based_recovery`: fixed formulas reduce the injected network and stress pressure. This phase tests recovery-state rendering; it is not a learned controller or evidence of human recovery.

## API Surface

- `GET /simulation/telemetry-profile` returns simulator capabilities and phases.
- `GET /simulation/telemetry-preview` returns a short preview of generated frames.
- `WS /ws/telemetry` streams live frames with `simulator_state` included.

## Research Value

This gives the dashboard a realistic live intelligence layer while preserving a clean path to real sensors later. Hardware integrations can replace individual generators without changing the dashboard contract.
