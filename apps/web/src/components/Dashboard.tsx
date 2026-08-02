import type { CSSProperties } from 'react'
import type {
  AnalyticsPayload,
  EventWindow,
  ExperimentSession,
  PlatformArchitecture,
  TelemetryEvent,
} from '../types'

const metricLabels: Record<string, string> = {
  embodiment: 'Embodiment',
  presence: 'Presence',
  performance: 'Performance',
  behavior: 'Behavior',
  physiological: 'Physiological',
  system: 'System',
  visualization: 'Visualization',
}

const catemLayerLabels: Record<string, string> = {
  experience: 'Experience',
  action: 'Action',
  human_state: 'Human state & cognition',
  system: 'System conditions',
  data_interpretation: 'Data & interpretation conditions',
}

const rawMetrics = [
  ['task_completion_time', 'Task time', 's'],
  ['error_rate', 'Error rate', '%'],
  ['heart_rate', 'Heart rate', 'bpm'],
  ['hrv', 'HRV', 'ms'],
  ['latency', 'Latency', 'ms'],
  ['fps', 'FPS', ''],
  ['packet_loss', 'Packet loss', '%'],
]

const graphNodes = [
  ['Agency', 'agency'],
  ['Ownership', 'ownership'],
  ['Presence', 'presence'],
  ['Latency', 'latency'],
  ['Stress', 'heart_rate'],
  ['Performance', 'task_efficiency'],
]

interface ScoreBarProps {
  label: string
  score: number
  level: string
  coverage?: number
  missingMetrics?: string[]
}

function ScoreBar({ label, score, level, coverage, missingMetrics = [] }: ScoreBarProps) {
  return (
    <article className="score-card">
      <div className="score-card__heading">
        <span>{label}</span>
        <strong>{score}</strong>
      </div>
      <div className="bar-track" aria-label={`${label} score ${score}`}>
        <div className={`bar-fill ${level}`} style={{ width: `${Math.min(score, 100)}%` }} />
      </div>
      <small>
        {level}
        {coverage !== undefined ? ` · ${coverage}% coverage` : ''}
      </small>
      {missingMetrics.length > 0 && (
        <p className="missing-metrics">Missing: {missingMetrics.join(', ')}</p>
      )}
    </article>
  )
}

function TrendRow({ session }: { session: ExperimentSession }) {
  const score = session.scores.overall
  return (
    <tr>
      <td>{session.participant_id}</td>
      <td>{session.task_type}</td>
      <td>{session.metrics.latency ?? 'n/a'}</td>
      <td>{session.metrics.error_rate ?? 'n/a'}</td>
      <td>{score}</td>
    </tr>
  )
}

function LiveMetric({ label, value, unit }: { label: string; value?: number | string | null; unit: string }) {
  return (
    <div className="live-metric">
      <span>{label}</span>
      <strong>
        {value ?? 'waiting'}
        {value !== undefined && value !== null && unit ? ` ${unit}` : ''}
      </strong>
    </div>
  )
}

interface DashboardProps {
  latest: ExperimentSession
  sessions: ExperimentSession[]
  analytics?: AnalyticsPayload
  architecture: PlatformArchitecture | null
  telemetry: TelemetryEvent | null
  telemetryHistory: TelemetryEvent[]
  streamState: 'connecting' | 'live' | 'offline'
  eventWindow: EventWindow | null
}

function SignalStrip({ label, values, unit }: { label: string; values: number[]; unit: string }) {
  const latestValue = values.at(-1)
  const maxValue = Math.max(...values, 1)

  return (
    <div className="signal-strip">
      <div className="signal-strip__heading">
        <span>{label}</span>
        <strong>{latestValue !== undefined ? `${Math.round(latestValue)}${unit}` : 'waiting'}</strong>
      </div>
      <div className="signal-bars">
        {values.slice(-30).map((value, index) => (
          <i
            key={`${label}-${index}-${value}`}
            style={{ height: `${Math.max(8, (value / maxValue) * 100)}%` }}
          />
        ))}
      </div>
    </div>
  )
}

function LiveTimeline({ history }: { history: TelemetryEvent[] }) {
  const events = history.slice(-6).reverse()

  return (
    <div className="live-timeline">
      {events.length ? events.map((event, index) => {
        const latency = Math.round(event.metrics.latency ?? 0)
        const stability = Math.round(event.cognitive_state.cognitive_stability)
        const risk = event.risk_events[0]?.type || event.embodiment_prediction.state
        return (
          <span key={`${event.timestamp}-${index}`}>
            {new Date(event.timestamp).toLocaleTimeString()} / {latency}ms / stability {stability}% / {risk}
          </span>
        )
      }) : <span>Awaiting live telemetry frames</span>}
    </div>
  )
}

const eventMetricRows = [
  ['agency', 'Experience', 'Agency'],
  ['task_error', 'Action', 'Task error'],
  ['workload', 'Human state', 'Workload'],
  ['heart_rate', 'Human state', 'Heart rate'],
  ['latency', 'System', 'Latency'],
  ['packet_loss', 'System', 'Packet loss'],
  ['tracking_dropout', 'System', 'Tracking dropout'],
] as const

function EventWindowPanel({ eventWindow }: { eventWindow: EventWindow }) {
  return (
    <section id="object-drop-window" className="panel event-window-panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Selected evidence window</p>
          <h2>{eventWindow.event_name}</h2>
        </div>
        <span>
          {eventWindow.window_seconds[0]}s to +{eventWindow.window_seconds[1]}s · synthetic fixture
        </span>
      </div>
      <div className="event-table-wrap">
        <table className="event-window-table">
          <thead>
            <tr>
              <th>Layer / measure</th>
              {eventWindow.samples.map((sample) => (
                <th className={sample.offset_seconds === 0 ? 'event-moment' : ''} key={sample.offset_seconds}>
                  {sample.offset_seconds > 0 ? '+' : ''}{sample.offset_seconds}s
                </th>
              ))}
              <th>Source</th>
            </tr>
          </thead>
          <tbody>
            {eventMetricRows.map(([metric, layer, label]) => {
              const record = eventWindow.records.find((item) => item.metric === metric)
              return (
                <tr key={metric}>
                  <td>
                    <span>{layer}</span>
                    <strong>{label}</strong>
                  </td>
                  {eventWindow.samples.map((sample) => (
                    <td className={sample.offset_seconds === 0 ? 'event-moment' : ''} key={sample.offset_seconds}>
                      {sample.metrics[metric]}
                      {record?.unit && record.unit !== 'instrument_defined' && record.unit !== 'binary'
                        ? ` ${record.unit}`
                        : ''}
                    </td>
                  ))}
                  <td><code>{record?.source || 'unreported'}</code></td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
      <p className="interpretation-boundary">{eventWindow.interpretation_boundary}</p>
    </section>
  )
}

function Dashboard({
  latest,
  sessions,
  analytics,
  architecture,
  telemetry,
  telemetryHistory,
  streamState,
  eventWindow,
}: DashboardProps) {
  if (!latest) {
    return <div className="loading">No sessions available yet.</div>
  }

  const activeSession = telemetry
    ? sessions.find((session) => session.participant_id === telemetry.participant_id) || latest
    : latest
  const categories = activeSession.scores.categories
  const liveMetrics = telemetry?.metrics || latest.metrics
  const liveRisks = telemetry?.risk_events || latest.risk_events || []
  const livePrediction = telemetry?.embodiment_prediction || latest.embodiment_prediction
  const cognitive = telemetry?.cognitive_state || latest.cognitive_state
  const forecast = telemetry?.failure_forecast || latest.failure_forecast
  const explanations = telemetry?.prediction_explanation || latest.prediction_explanation || []
  const consciousness = telemetry?.embodied_consciousness || latest.embodied_consciousness
  const digitalTwin = telemetry?.human_digital_twin || latest.human_digital_twin
  const memoryGraph = telemetry?.embodied_memory_graph || latest.embodied_memory_graph
  const tlm = telemetry?.tlm_interpretation || latest.tlm_interpretation
  const realitySync = telemetry?.reality_sync || latest.reality_sync
  const scientist = telemetry?.autonomous_scientist || latest.autonomous_scientist
  const presence = telemetry?.post_screen_experience || latest.post_screen_experience
  const catem = telemetry?.catem || latest.catem
  const observationalLayers = Object.entries(catem?.layers || {}).filter(
    ([key]) => key !== 'data_interpretation',
  )
  const interpretationConditions = catem?.layers?.data_interpretation
  const simulatorState = telemetry?.simulator_state
  const signalHistory = telemetryHistory.length ? telemetryHistory : telemetry ? [telemetry] : []
  const latencySeries = signalHistory.map((event) => event.metrics.latency ?? 0)
  const cognitiveSeries = signalHistory.map((event) => event.cognitive_state.cognitive_stability)
  const embodimentSeries = signalHistory.map((event) => event.embodiment_prediction.predicted_embodiment_quality)
  const riskSeries = signalHistory.map((event) => event.risk_events.length * 25 + event.cognitive_state.collapse_risk_score)

  return (
    <div className="dashboard-grid">
      <section className="summary-panel">
        <div>
          <p className="eyebrow">Mission control / <span className={`stream-dot ${streamState}`}>{streamState}</span></p>
          <h2>{activeSession.participant_id}</h2>
          <p>{activeSession.task_type}</p>
          <p>{activeSession.setup}</p>
        </div>
        <div className="quality-score">
          <span>{cognitive?.cognitive_stability ?? latest.scores.overall}</span>
          <small>cognitive stability</small>
        </div>
      </section>

      <section className="hero-visual">
        <div className="orbital-map">
          {graphNodes.map(([label, key], index) => {
            const value = Math.min(100, Math.max(0, liveMetrics[key] ?? 50))
            return (
              <div
                className="graph-node"
                key={key}
                style={{
                  '--angle': `${index * 60}deg`,
                  '--pulse': `${value}%`,
                } as CSSProperties}
              >
                <strong>{Math.round(value)}</strong>
                <span>{label}</span>
              </div>
            )
          })}
          <div className="graph-core">
            <strong>{livePrediction?.state || 'stable'}</strong>
            <span>Embodiment graph</span>
          </div>
        </div>
        <div className="timeline-strip">
          <LiveTimeline history={signalHistory} />
        </div>
      </section>

      <section className="panel catem-overview">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">PDF-derived evaluation framework</p>
            <h2>CATEM Cross-Layer Assessment</h2>
          </div>
          <span>evidence-condition profile</span>
        </div>
        <div className="catem-layer-grid">
          {observationalLayers.map(([key, layer]) => (
            <ScoreBar
              key={key}
              label={catemLayerLabels[key] || key}
              score={layer.score}
              level={layer.level}
              coverage={layer.coverage}
              missingMetrics={layer.missing_metrics}
            />
          ))}
        </div>
        {interpretationConditions && (
          <div className="interpretation-condition-band">
            <div>
              <span className="interpretation-condition-symbol">𝒟t</span>
              <div>
                <strong>Data &amp; interpretation conditions</strong>
                <small>Cross-cutting record metadata · not an observational layer</small>
              </div>
            </div>
            <div className="interpretation-condition-score">
              <strong>{interpretationConditions.score}</strong>
              <span>{interpretationConditions.level} · {interpretationConditions.coverage}% coverage</span>
            </div>
          </div>
        )}
        <div className="evidence-strip">
          <LiveMetric label="Metric coverage" value={catem?.evidence_profile?.field_coverage} unit="%" />
          <LiveMetric label="Synchronization" value={catem?.evidence_profile?.synchronization_quality} unit="%" />
          <LiveMetric label="Missing data" value={catem?.evidence_profile?.missing_data_burden} unit="%" />
        </div>
      </section>

      {eventWindow && <EventWindowPanel eventWindow={eventWindow} />}

      <section className="panel catem-propositions">
        <div className="panel-heading">
          <h2>CATEM Propositions P1–P6</h2>
          <span>live cross-layer tests</span>
        </div>
        <div className="proposition-grid">
          {catem?.propositions?.map((proposition) => (
            <article className="proposition-card" key={proposition.id}>
              <div>
                <strong>{proposition.id}</strong>
                <span className={proposition.status}>{proposition.status}</span>
              </div>
              <h3>{proposition.name}</h3>
              <p>{proposition.evidence}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="panel catem-recommendations">
        <div className="panel-heading">
          <h2>Agency-Preserving Adaptation</h2>
          <span>explainable and overridable</span>
        </div>
        <div className="action-list">
          {catem?.adaptive_recommendations?.map((recommendation) => (
            <span key={recommendation}>{recommendation}</span>
          ))}
        </div>
      </section>

      <section className="panel stream-wall">
        <div className="panel-heading">
          <h2>Live Cognitive Streams</h2>
          <span>{signalHistory.length} frames buffered</span>
        </div>
        <div className="stream-grid">
          <SignalStrip label="Latency" values={latencySeries} unit="ms" />
          <SignalStrip label="Cognitive stability" values={cognitiveSeries} unit="%" />
          <SignalStrip label="Embodiment prediction" values={embodimentSeries} unit="%" />
          <SignalStrip label="Risk energy" values={riskSeries} unit="%" />
        </div>
      </section>

      <section className="panel simulator-panel">
        <div className="panel-heading">
          <h2>Real Telemetry Simulator</h2>
          <span>{simulatorState?.phase?.replaceAll('_', ' ') || 'warming up'}</span>
        </div>
        <div className="simulator-phase">
          <div
            className="simulator-phase__fill"
            style={{
              width: `${simulatorState ? Math.min(100, (simulatorState.phase_tick / simulatorState.cycle_length) * 100) : 0}%`,
            }}
          />
        </div>
        <div className="simulator-grid">
          <div>
            <strong>Physiology</strong>
            <LiveMetric label="HR" value={simulatorState?.physiological?.heart_rate} unit="bpm" />
            <LiveMetric label="HRV" value={simulatorState?.physiological?.hrv} unit="ms" />
            <LiveMetric label="Stress" value={simulatorState?.physiological?.stress_index} unit="%" />
          </div>
          <div>
            <strong>Network</strong>
            <LiveMetric label="Latency" value={simulatorState?.network?.latency} unit="ms" />
            <LiveMetric label="Jitter" value={simulatorState?.network?.jitter} unit="ms" />
            <LiveMetric label="Loss" value={simulatorState?.network?.packet_loss} unit="%" />
          </div>
          <div>
            <strong>Embodiment</strong>
            <LiveMetric label="Agency" value={simulatorState?.embodiment?.agency} unit="%" />
            <LiveMetric label="Ownership" value={simulatorState?.embodiment?.ownership} unit="%" />
            <LiveMetric label="Degrade" value={simulatorState?.embodiment?.degradation} unit="%" />
          </div>
          <div>
            <strong>Stress Escalation</strong>
            <LiveMetric label="Workload" value={simulatorState?.stress?.workload} unit="%" />
            <LiveMetric label="Errors" value={simulatorState?.stress?.error_rate} unit="%" />
            <LiveMetric label="Timing" value={simulatorState?.stress?.interaction_timing_variance} unit="ms" />
          </div>
        </div>
      </section>

      <section className="panel presence-panel">
        <div className="panel-heading">
          <h2>Multimodal Presence Panel</h2>
          <span>{presence?.neural_presence?.state}</span>
        </div>
        <div className="cognitive-grid">
          <LiveMetric label="Presence" value={presence?.neural_presence?.presence_transmission} unit="%" />
          <LiveMetric label="Intention" value={presence?.neural_presence?.intention_clarity} unit="%" />
          <LiveMetric label="Emotion" value={presence?.neural_presence?.emotional_bandwidth} unit="%" />
          <LiveMetric label="Embodiment" value={presence?.neural_presence?.embodiment_signal} unit="%" />
        </div>
      </section>

      <section className="panel companion-panel">
        <div className="panel-heading">
          <h2>Adaptive Support Panel</h2>
          <span>{presence?.ai_companion?.tone}</span>
        </div>
        <div className="research-sentence">{presence?.ai_companion?.message}</div>
        <div className="action-list">
          {presence?.ai_companion?.interventions?.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Longitudinal Session Profile</h2>
          <span>{presence?.persistent_digital_self?.continuity_score}% continuity</span>
        </div>
        <div className="research-sentence">{presence?.persistent_digital_self?.memory_aware_summary}</div>
        <div className="metric-list">
          <div className="metric-row">
            <span>Stability mode</span>
            <strong>{presence?.persistent_digital_self?.embodiment_preferences?.stability_mode}</strong>
          </div>
          <div className="metric-row">
            <span>Preferred recovery</span>
            <strong>{presence?.persistent_digital_self?.embodiment_preferences?.preferred_recovery}</strong>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Full-Sensory Telepresence</h2>
          <span>{presence?.sensory_presence?.full_sensory_presence}% fidelity</span>
        </div>
        <div className="cognitive-grid">
          <LiveMetric label="Haptics" value={presence?.sensory_presence?.haptic_fidelity} unit="%" />
          <LiveMetric label="Visual" value={presence?.sensory_presence?.visual_fidelity} unit="%" />
          <LiveMetric label="Audio" value={presence?.sensory_presence?.spatial_audio_fidelity} unit="%" />
          <LiveMetric label="Tactile" value={presence?.sensory_presence?.tactile_presence} unit="%" />
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Shared Reality Space</h2>
          <span>{presence?.shared_reality?.space_state}</span>
        </div>
        <div className="cognitive-grid">
          <LiveMetric label="Trust" value={presence?.shared_reality?.collaboration_trust} unit="%" />
          <LiveMetric label="Team load" value={presence?.shared_reality?.team_cognitive_load} unit="%" />
          <LiveMetric label="Social sync" value={presence?.shared_reality?.social_presence_sync} unit="%" />
          <LiveMetric label="Augment" value={presence?.cognitive_augmentation?.control_precision_gain} unit="%" />
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Adaptation Control Panel</h2>
          <span>{presence?.reality_orchestration?.sensory_fidelity_target}</span>
        </div>
        <div className="research-sentence">{presence?.reality_orchestration?.orchestration_goal}</div>
        <div className="action-list">
          {presence?.reality_orchestration?.active_actions?.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </section>

      <section className="score-grid">
        {Object.entries(categories).map(([key, value]) => (
          <ScoreBar
            key={key}
            label={metricLabels[key] || key}
            score={value.score}
            level={value.level}
          />
        ))}
      </section>

      <section className="panel live-panel">
        <div className="panel-heading">
          <h2>Real-Time Multimodal Stream</h2>
          <span>{telemetry ? telemetry.source : 'stored session'}</span>
        </div>
        <div className="live-grid">
          <LiveMetric label="Latency" value={liveMetrics.latency} unit="ms" />
          <LiveMetric label="Packet loss" value={liveMetrics.packet_loss} unit="%" />
          <LiveMetric label="Heart rate" value={liveMetrics.heart_rate} unit="bpm" />
          <LiveMetric label="Agency" value={liveMetrics.agency} unit="" />
        </div>
        <div className="embodiment-graph">
          <div>
            <span>Predicted embodiment</span>
            <strong>{livePrediction?.predicted_embodiment_quality ?? 'n/a'}</strong>
          </div>
          <div className="bar-track">
            <div
              className={`bar-fill ${livePrediction?.state === 'stable' ? 'high' : 'medium'}`}
              style={{ width: `${Math.min(livePrediction?.predicted_embodiment_quality || 0, 100)}%` }}
            />
          </div>
          <small>{livePrediction?.state || 'waiting for stream'}</small>
        </div>
      </section>

      <section className="panel cognitive-panel">
        <div className="panel-heading">
          <h2>Cognitive State Engine</h2>
          <span>{cognitive?.immersion_collapse_risk} instability heuristic</span>
        </div>
        <div className="cognitive-grid">
          <LiveMetric label="Stability" value={cognitive?.cognitive_stability} unit="%" />
          <LiveMetric label="Instability heuristic" value={cognitive?.collapse_risk_score} unit="%" />
          <LiveMetric label="Attention drift" value={cognitive?.attention_drift} unit="%" />
          <LiveMetric label="Stress" value={cognitive?.stress_escalation} unit="" />
        </div>
      </section>

      <section className="panel forecast-panel">
        <div className="panel-heading">
          <h2>Failure Forecast Heuristic</h2>
          <span>{Math.round((forecast?.confidence || 0) * 100)}% confidence</span>
        </div>
        <div className="forecast-callout">
          <strong>{forecast?.prediction}</strong>
          <span>
            {forecast?.time_to_event_seconds
              ? `Predicted in ${forecast.time_to_event_seconds} seconds`
              : 'Control envelope remains stable'}
          </span>
        </div>
        <div className="action-list">
          {forecast?.adaptive_actions?.map((action) => (
            <span key={action}>{action}</span>
          ))}
        </div>
      </section>

      <section className="panel consciousness-panel">
        <div className="panel-heading">
          <h2>Embodied-State Summary</h2>
          <span>{consciousness?.state}</span>
        </div>
        <div className="cognitive-grid">
          <LiveMetric label="Awareness" value={consciousness?.awareness} unit="%" />
          <LiveMetric label="Attention" value={consciousness?.attention} unit="%" />
          <LiveMetric label="Control" value={consciousness?.control_confidence} unit="%" />
          <LiveMetric label="Continuity" value={consciousness?.presence_continuity} unit="%" />
        </div>
      </section>

      <section className="panel twin-panel">
        <div className="panel-heading">
          <h2>Participant-State Profile</h2>
          <span>{digitalTwin?.adaptation_profile}</span>
        </div>
        <div className="metric-list">
          <div className="metric-row">
            <span>Fatigue index</span>
            <strong>{digitalTwin?.fatigue_index}%</strong>
          </div>
          <div className="metric-row">
            <span>Latency sensitivity</span>
            <strong>{digitalTwin?.embodiment_fingerprint?.latency_sensitivity}</strong>
          </div>
          <div className="metric-row">
            <span>Recovery strategy</span>
            <strong>{digitalTwin?.embodiment_fingerprint?.recovery_strategy}</strong>
          </div>
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Reality Synchronization Engine</h2>
          <span>{realitySync?.orchestration_state}</span>
        </div>
        <div className="cognitive-grid">
          <LiveMetric label="Robot" value={realitySync?.physical_robot_sync} unit="%" />
          <LiveMetric label="VR world" value={realitySync?.vr_world_sync} unit="%" />
          <LiveMetric label="Body state" value={realitySync?.body_state_sync} unit="%" />
          <LiveMetric label="Unified" value={realitySync?.unified_reality_score} unit="%" />
        </div>
      </section>

      <section className="panel tlm-panel">
        <div className="panel-heading">
          <h2>Narrative Summary Module</h2>
          <span>{tlm?.latent_state}</span>
        </div>
        <div className="research-sentence">{tlm?.research_sentence}</div>
        <div className="timeline-mini">
          {tlm?.reasoning_trace?.map((line) => (
            <span key={line}>{line}</span>
          ))}
        </div>
      </section>

      <section className="panel risk-panel">
        <div className="panel-heading">
          <h2>Risk Rule Monitor</h2>
          <span>{liveRisks.length} active</span>
        </div>
        <div className="relationship-list">
          {liveRisks.length ? (
            liveRisks.map((risk) => (
              <div className="relationship" key={risk.type}>
                <span className={risk.severity}>{risk.severity}</span>
                <p>{risk.type}: {risk.detail}</p>
              </div>
            ))
          ) : (
            <div className="empty-state">No active risk signals in the current stream.</div>
          )}
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Hypothesis Prompt Generator</h2>
          <span>rule-based prompt</span>
        </div>
        <div className="research-sentence">{scientist?.hypothesis}</div>
        <div className="empty-state">{scientist?.suggested_experiment}</div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Session Pattern Summary</h2>
          <span>{memoryGraph?.memory_strength}% strength</span>
        </div>
        <div className="action-list">
          {memoryGraph?.past_failure_patterns?.map((pattern) => (
            <span key={pattern}>{pattern}</span>
          ))}
        </div>
        <div className="action-list">
          {memoryGraph?.successful_recovery_strategies?.map((strategy) => (
            <span key={strategy}>{strategy}</span>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Explanation Trace</h2>
          <span>{explanations.length} active factors</span>
        </div>
        <div className="metric-list">
          {explanations.length ? explanations.map((item) => (
            <div className="metric-row" key={item.factor}>
              <span>{item.factor}: {item.detail}</span>
              <strong>{Math.round(item.impact * 100)}%</strong>
            </div>
          )) : <div className="empty-state">Prediction model is not flagging dominant degradation factors.</div>}
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Core Metrics</h2>
          <span>{latest.session_time}</span>
        </div>
        <div className="metric-list">
          {rawMetrics.map(([key, label, unit]) => (
            <div className="metric-row" key={key}>
              <span>{label}</span>
              <strong>
                {latest.metrics[key] ?? 'n/a'}
                {latest.metrics[key] !== undefined && unit ? ` ${unit}` : ''}
              </strong>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Relationships</h2>
          <span>{sessions.length} sessions</span>
        </div>
        <div className="relationship-list">
          {analytics?.relationships?.map((item) => (
            <div className="relationship" key={item.label}>
              <span className={item.status}>{item.status}</span>
              <p>{item.label}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Research Analytics</h2>
          <span>descriptive correlations with sample size</span>
        </div>
        <div className="metric-list">
          {analytics?.correlations?.map((item) => (
            <div className="metric-row" key={`${item.x}-${item.y}`}>
              <span>{item.x} vs {item.y}</span>
              <strong>{item.n < 3 ? `insufficient n (${item.n})` : `${item.pearson_r ?? 'n/a'} (n=${item.n})`}</strong>
            </div>
          ))}
        </div>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <h2>Platform Pipeline</h2>
          <span>{architecture?.research_modules?.length || 0} modules</span>
        </div>
        <div className="pipeline-list">
          {architecture?.pipeline?.map((step, index) => (
            <div className="pipeline-step" key={step}>
              <strong>{index + 1}</strong>
              <span>{step}</span>
            </div>
          ))}
        </div>
      </section>

      <section className="panel table-panel">
        <div className="panel-heading">
          <h2>Session and Fixture Runs</h2>
          <span>descriptive comparison</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Session ID</th>
              <th>Task</th>
              <th>Latency</th>
              <th>Errors</th>
              <th>Quality</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map((session) => (
              <TrendRow key={session.id} session={session} />
            ))}
          </tbody>
        </table>
      </section>
    </div>
  )
}

export default Dashboard
