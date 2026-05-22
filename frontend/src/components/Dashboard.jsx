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

function Dashboard({ latest, sessions, analytics }) {
  if (!latest) {
    return <div className="loading">No sessions available yet.</div>
  }

  const categories = latest.scores.categories

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
