import React from 'react'

const metricLabels = {
  embodiment: 'Embodiment',
  presence: 'Presence',
  performance: 'Performance',
  behavior: 'Behavior',
  physiological: 'Physiological',
  system: 'System',
  visualization: 'Visualization',
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

function ScoreBar({ label, score, level }) {
  return (
    <article className="score-card">
      <div className="score-card__heading">
        <span>{label}</span>
        <strong>{score}</strong>
      </div>
      <div className="bar-track" aria-label={`${label} score ${score}`}>
        <div className={`bar-fill ${level}`} style={{ width: `${Math.min(score, 100)}%` }} />
      </div>
      <small>{level}</small>
    </article>
  )
}

function TrendRow({ session }) {
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

function LiveMetric({ label, value, unit }) {
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

function Dashboard({ latest, sessions, analytics, architecture, telemetry }) {
  if (!latest) {
    return <div className="loading">No sessions available yet.</div>
  }

  const categories = latest.scores.categories
  const liveMetrics = telemetry?.metrics || latest.metrics
  const liveRisks = telemetry?.risk_events || latest.risk_events || []
  const livePrediction = telemetry?.embodiment_prediction || latest.embodiment_prediction

  return (
    <div className="dashboard-grid">
      <section className="summary-panel">
        <div>
          <p className="eyebrow">Latest session</p>
          <h2>{latest.participant_id}</h2>
          <p>{latest.task_type}</p>
          <p>{latest.setup}</p>
        </div>
        <div className="quality-score">
          <span>{latest.scores.overall}</span>
          <small>{latest.scores.overall_level} quality</small>
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

      <section className="panel risk-panel">
        <div className="panel-heading">
          <h2>Intelligent Risk Detection</h2>
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
          <span>Pearson correlations</span>
        </div>
        <div className="metric-list">
          {analytics?.correlations?.map((item) => (
            <div className="metric-row" key={`${item.x}-${item.y}`}>
              <span>{item.x} vs {item.y}</span>
              <strong>{item.pearson_r ?? 'n/a'}</strong>
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
          <h2>Experiment Runs</h2>
          <span>participant comparison</span>
        </div>
        <table>
          <thead>
            <tr>
              <th>Participant</th>
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
