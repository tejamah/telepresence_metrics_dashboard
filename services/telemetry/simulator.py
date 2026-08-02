from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any


def _clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))


def _round_metric(value: float) -> float:
    return round(value, 2)


@dataclass(frozen=True)
class SimulatorPhase:
    name: str
    stress_pressure: float
    network_pressure: float
    recovery_pressure: float


class PhysiologicalSimulator:
    def generate(self, base: dict[str, float], tick: int, phase: SimulatorPhase) -> dict[str, float]:
        cardiac_rhythm = math.sin(tick / 3.8) * 2.8
        breathing_rhythm = math.sin(tick / 5.2) * 1.6
        stress_pressure = phase.stress_pressure * 18
        recovery = phase.recovery_pressure * 7
        heart_rate = _clamp(base.get("heart_rate", 86) + cardiac_rhythm + stress_pressure - recovery, 62, 138)
        hrv = _clamp(base.get("hrv", 54) - phase.stress_pressure * 18 - phase.network_pressure * 4 + recovery, 18, 92)
        respiration_rate = _clamp(13.5 + breathing_rhythm + phase.stress_pressure * 6, 10, 28)
        galvanic_response = _clamp(0.25 + phase.stress_pressure * 0.55 + abs(math.sin(tick / 6)) * 0.18, 0.1, 1.0)
        return {
            "heart_rate": _round_metric(heart_rate),
            "hrv": _round_metric(hrv),
            "respiration_rate": _round_metric(respiration_rate),
            "galvanic_response": _round_metric(galvanic_response),
        }


class NetworkSimulator:
    def generate(self, base: dict[str, float], tick: int, phase: SimulatorPhase) -> dict[str, float]:
        jitter_wave = abs(math.sin(tick / 2.4)) * 8
        spike = phase.network_pressure * 72
        latency = _clamp(base.get("latency", 72) + math.sin(tick / 3.1) * 13 + spike - phase.recovery_pressure * 22, 28, 245)
        packet_loss = _clamp(base.get("packet_loss", 0.9) + phase.network_pressure * 5.8 + math.cos(tick / 4.4) * 0.45, 0, 11)
        jitter = _clamp(5 + jitter_wave + phase.network_pressure * 35, 1, 70)
        fps = _clamp(base.get("fps", 74) - phase.network_pressure * 28 - phase.stress_pressure * 4 + phase.recovery_pressure * 8, 24, 100)
        bandwidth = _clamp(72 - phase.network_pressure * 44 + phase.recovery_pressure * 10 + math.sin(tick / 7) * 3, 8, 95)
        return {
            "latency": _round_metric(latency),
            "packet_loss": _round_metric(packet_loss),
            "jitter": _round_metric(jitter),
            "fps": _round_metric(fps),
            "bandwidth_mbps": _round_metric(bandwidth),
            "compression_level": _round_metric(_clamp(18 + phase.network_pressure * 58 - phase.recovery_pressure * 12, 8, 88)),
        }


class EmbodimentDegradationSimulator:
    def generate(self, base: dict[str, float], network: dict[str, float], physiology: dict[str, float], tick: int) -> dict[str, float]:
        latency_penalty = max(0, network["latency"] - 70) * 0.16
        packet_penalty = network["packet_loss"] * 2.8
        stress_penalty = max(0, physiology["heart_rate"] - 92) * 0.22
        visual_penalty = max(0, 65 - network["fps"]) * 0.45
        micro_recovery = math.cos(tick / 8) * 2.2
        agency = _clamp(base.get("agency", 74) - latency_penalty - packet_penalty - stress_penalty + micro_recovery, 20, 96)
        ownership = _clamp(base.get("ownership", 68) - latency_penalty * 0.72 - visual_penalty - network["jitter"] * 0.08, 18, 95)
        presence = _clamp(base.get("presence", 70) - latency_penalty * 0.55 - visual_penalty * 0.75 + micro_recovery, 22, 96)
        embodiment = _clamp((agency * 0.34) + (ownership * 0.33) + (presence * 0.33), 20, 98)
        haptic_delay = _clamp(base.get("haptic_delay", 58) + network["latency"] * 0.35 + network["jitter"] * 0.55, 18, 240)
        return {
            "agency": _round_metric(agency),
            "ownership": _round_metric(ownership),
            "presence": _round_metric(presence),
            "embodiment": _round_metric(embodiment),
            "visual_match": _round_metric(_clamp(base.get("visual_match", 74) - visual_penalty - network["packet_loss"] * 1.8, 18, 96)),
            "haptic_delay": _round_metric(haptic_delay),
            "gaze_stability": _round_metric(_clamp(92 - latency_penalty - stress_penalty * 0.8 - network["jitter"] * 0.2, 25, 98)),
            "motion_entropy": _round_metric(_clamp(18 + latency_penalty * 0.8 + stress_penalty * 1.2 + abs(math.sin(tick / 2.9)) * 8, 6, 86)),
        }


class StressEscalationSimulator:
    def generate(
        self,
        base: dict[str, float],
        physiology: dict[str, float],
        network: dict[str, float],
        embodiment: dict[str, float],
        phase: SimulatorPhase,
    ) -> dict[str, float]:
        workload = _clamp(
            base.get("workload", 56)
            + phase.stress_pressure * 24
            + max(0, network["latency"] - 95) * 0.11
            + max(0, 65 - embodiment["agency"]) * 0.18
            - phase.recovery_pressure * 10,
            22,
            96,
        )
        stress_index = _clamp(
            workload * 0.42
            + max(0, physiology["heart_rate"] - 80) * 0.55
            + max(0, 52 - physiology["hrv"]) * 0.48
            + network["packet_loss"] * 2.2,
            5,
            100,
        )
        error_rate = _clamp(base.get("error_rate", 7) + max(0, workload - 62) * 0.22 + network["packet_loss"] * 0.7, 0, 38)
        interaction_variance = _clamp(8 + network["jitter"] * 0.9 + stress_index * 0.22, 4, 90)
        safety_events = _clamp(base.get("safety_events", 0) + (1 if stress_index > 68 else 0) + (1 if network["latency"] > 155 else 0), 0, 8)
        return {
            "workload": _round_metric(workload),
            "stress_index": _round_metric(stress_index),
            "error_rate": _round_metric(error_rate),
            "interaction_timing_variance": _round_metric(interaction_variance),
            "safety_events": _round_metric(safety_events),
        }


class TelemetrySimulator:
    def __init__(self) -> None:
        self.physiology = PhysiologicalSimulator()
        self.network = NetworkSimulator()
        self.embodiment = EmbodimentDegradationSimulator()
        self.stress = StressEscalationSimulator()

    def phase_for_tick(self, tick: int) -> SimulatorPhase:
        cycle = tick % 48
        if cycle < 12:
            return SimulatorPhase("baseline_alignment", stress_pressure=0.16, network_pressure=0.12, recovery_pressure=0.35)
        if cycle < 24:
            pressure = (cycle - 12) / 12
            return SimulatorPhase("network_degradation", stress_pressure=0.25 + pressure * 0.18, network_pressure=0.35 + pressure * 0.55, recovery_pressure=0.05)
        if cycle < 36:
            pressure = (cycle - 24) / 12
            return SimulatorPhase("stress_escalation", stress_pressure=0.52 + pressure * 0.36, network_pressure=0.55, recovery_pressure=0.0)
        pressure = (cycle - 36) / 12
        return SimulatorPhase("rule_based_recovery", stress_pressure=0.45 - pressure * 0.28, network_pressure=0.4 - pressure * 0.26, recovery_pressure=0.35 + pressure * 0.45)

    def simulate(self, base: dict[str, float], tick: int) -> tuple[dict[str, float], dict[str, Any]]:
        phase = self.phase_for_tick(tick)
        physiology = self.physiology.generate(base, tick, phase)
        network = self.network.generate(base, tick, phase)
        embodiment = self.embodiment.generate(base, network, physiology, tick)
        stress = self.stress.generate(base, physiology, network, embodiment, phase)
        task_efficiency = _clamp(
            base.get("task_efficiency", 74)
            - stress["error_rate"] * 0.55
            - max(0, network["latency"] - 90) * 0.05
            + phase.recovery_pressure * 6,
            25,
            96,
        )
        collaboration = _clamp(base.get("collaboration_quality", 72) - stress["stress_index"] * 0.12 + embodiment["presence"] * 0.08, 20, 96)
        metrics = {
            **base,
            **physiology,
            **network,
            **embodiment,
            **stress,
            "task_efficiency": _round_metric(task_efficiency),
            "collaboration_quality": _round_metric(collaboration),
        }
        simulator_state = {
            "phase": phase.name,
            "phase_tick": tick % 48,
            "cycle_length": 48,
            "physiological": {
                "heart_rate": metrics["heart_rate"],
                "hrv": metrics["hrv"],
                "respiration_rate": metrics["respiration_rate"],
                "stress_index": metrics["stress_index"],
            },
            "network": {
                "latency": metrics["latency"],
                "jitter": metrics["jitter"],
                "packet_loss": metrics["packet_loss"],
                "bandwidth_mbps": metrics["bandwidth_mbps"],
            },
            "embodiment": {
                "agency": metrics["agency"],
                "ownership": metrics["ownership"],
                "presence": metrics["presence"],
                "degradation": _round_metric(100 - metrics["embodiment"]),
            },
            "stress": {
                "workload": metrics["workload"],
                "error_rate": metrics["error_rate"],
                "safety_events": metrics["safety_events"],
                "interaction_timing_variance": metrics["interaction_timing_variance"],
            },
            "generators": [
                "physiological simulator",
                "network simulator",
                "embodiment degradation simulator",
                "stress escalation simulator",
            ],
        }
        return metrics, simulator_state

    def profile(self) -> dict[str, Any]:
        return {
            "name": "Real Telemetry Simulator",
            "cycle_seconds": 48,
            "phases": [
                "baseline_alignment",
                "network_degradation",
                "stress_escalation",
                "rule_based_recovery",
            ],
            "simulators": {
                "physiological": ["heart_rate", "hrv", "respiration_rate", "galvanic_response"],
                "network": ["latency", "jitter", "packet_loss", "fps", "bandwidth_mbps"],
                "embodiment_degradation": ["agency", "ownership", "presence", "visual_match", "haptic_delay"],
                "stress_escalation": ["workload", "stress_index", "error_rate", "interaction_timing_variance", "safety_events"],
            },
        }
