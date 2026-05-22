export type MetricMap = Record<string, number>

export type Level = 'low' | 'medium' | 'high'

export interface ScoreCategory {
  score: number
  level: Level
}

export interface SessionScores {
  categories: Record<string, ScoreCategory>
  overall: number
  overall_level: Level
}

export interface RiskEvent {
  type: string
  severity: 'low' | 'medium' | 'high'
  detail: string
}

export interface EmbodimentPrediction {
  predicted_embodiment_quality: number
  immersion_breakdown_probability: number
  state: string
}

export interface CognitiveState {
  cognitive_stability: number
  immersion_collapse_risk: string
  collapse_risk_score: number
  attention_drift: number
  stress_escalation: string
}

export interface FailureForecast {
  prediction: string
  time_to_event_seconds: number | null
  confidence: number
  adaptive_actions: string[]
}

export interface ExplanationFactor {
  factor: string
  value: number
  impact: number
  detail: string
}

export interface AiSbomComponent {
  component: string
  type: string
  reliability: number
  runtime_reliability: number
  status: string
}

export interface AiSbom {
  components: AiSbomComponent[]
  dependency_risk: string
  degraded_count: number
}

export interface EmbodiedConsciousness {
  awareness: number
  attention: number
  control_confidence: number
  adaptation: number
  presence_continuity: number
  state: string
}

export interface HumanDigitalTwin {
  participant_id: string
  physiological_baseline: Record<string, number>
  fatigue_index: number
  adaptation_profile: string
  embodiment_fingerprint: Record<string, string>
}

export interface EmbodiedMemoryGraph {
  past_failure_patterns: string[]
  successful_recovery_strategies: string[]
  memory_strength: number
}

export interface TelepresenceLanguageModel {
  latent_state: string
  reasoning_trace: string[]
  adaptive_decision: string[]
  research_sentence: string
}

export interface RealitySyncState {
  physical_robot_sync: number
  vr_world_sync: number
  body_state_sync: number
  physiological_stream_sync: number
  unified_reality_score: number
  orchestration_state: string
}

export interface AutonomousScientist {
  observed: string
  hypothesis: string
  suggested_experiment: string
  analysis_plan: string[]
}

export interface PostScreenExperience {
  neural_presence: {
    presence_transmission: number
    intention_clarity: number
    emotional_bandwidth: number
    embodiment_signal: number
    state: string
  }
  persistent_digital_self: {
    identity: string
    continuity_score: number
    embodiment_preferences: Record<string, string>
    memory_aware_summary: string
  }
  ai_companion: {
    tone: string
    message: string
    interventions: string[]
    emotional_state_estimate: string
  }
  sensory_presence: {
    haptic_fidelity: number
    visual_fidelity: number
    spatial_audio_fidelity: number
    tactile_presence: number
    full_sensory_presence: number
  }
  shared_reality: {
    collaboration_trust: number
    team_cognitive_load: number
    social_presence_sync: number
    space_state: string
  }
  cognitive_augmentation: {
    mistake_prediction_risk: number
    focus_stabilization: number
    control_precision_gain: number
    augmentation_mode: string
  }
  reality_orchestration: {
    orchestration_goal: string
    active_actions: string[]
    environment_complexity: string
    sensory_fidelity_target: string
  }
}

export interface ExperimentSession {
  id: number
  participant_id: string
  task_type: string
  setup: string
  session_time: string
  metrics: MetricMap
  scores: SessionScores
  insight: string
  risk_events: RiskEvent[]
  embodiment_prediction: EmbodimentPrediction
  cognitive_state: CognitiveState
  prediction_explanation: ExplanationFactor[]
  failure_forecast: FailureForecast
  ai_sbom: AiSbom
  embodied_consciousness: EmbodiedConsciousness
  human_digital_twin: HumanDigitalTwin
  embodied_memory_graph: EmbodiedMemoryGraph
  tlm_interpretation: TelepresenceLanguageModel
  reality_sync: RealitySyncState
  autonomous_scientist: AutonomousScientist
  post_screen_experience: PostScreenExperience
}

export interface AnalyticsPayload {
  relationships: Array<{ label: string; status: string }>
  averages: MetricMap
  correlations: Array<{ x: string; y: string; pearson_r: number | null; n: number }>
  risk_counts: Record<string, number>
}

export interface MetricsPayload {
  latest: ExperimentSession
  sessions: ExperimentSession[]
  analytics: AnalyticsPayload
}

export interface PlatformArchitecture {
  name: string
  pipeline: string[]
  stream_sources: string[]
  research_modules: string[]
  simulator?: SimulatorProfile
}

export interface SimulatorProfile {
  name: string
  cycle_seconds: number
  phases: string[]
  simulators: Record<string, string[]>
}

export interface SimulatorState {
  phase: string
  phase_tick: number
  cycle_length: number
  physiological: Record<string, number>
  network: Record<string, number>
  embodiment: Record<string, number>
  stress: Record<string, number>
  generators: string[]
}

export interface TelemetryEvent {
  timestamp: string
  participant_id: string
  source: string
  metrics: MetricMap
  risk_events: RiskEvent[]
  embodiment_prediction: EmbodimentPrediction
  cognitive_state: CognitiveState
  prediction_explanation: ExplanationFactor[]
  failure_forecast: FailureForecast
  ai_sbom: AiSbom
  embodied_consciousness: EmbodiedConsciousness
  human_digital_twin: HumanDigitalTwin
  embodied_memory_graph: EmbodiedMemoryGraph
  tlm_interpretation: TelepresenceLanguageModel
  reality_sync: RealitySyncState
  autonomous_scientist: AutonomousScientist
  post_screen_experience: PostScreenExperience
  simulator_state?: SimulatorState
}
