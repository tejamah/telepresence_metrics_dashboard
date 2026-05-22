import React, { useEffect, useMemo, useState } from 'react'
import Dashboard from './components/Dashboard'
import './styles.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8010'
const WS_URL = API_URL.replace('http', 'ws')

function App() {
  const [data, setData] = useState(null)
  const [architecture, setArchitecture] = useState(null)
  const [telemetry, setTelemetry] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')

  const sessions = data?.sessions || []
  const latest = data?.latest || sessions.at(-1)

  const topInsight = useMemo(() => {
    if (telemetry?.failure_forecast?.prediction === 'teleoperation instability') {
      return `AI copilot predicts teleoperation instability in ${telemetry.failure_forecast.time_to_event_seconds}s with ${Math.round(telemetry.failure_forecast.confidence * 100)}% confidence.`
    }
    if (!sessions.length) return 'Upload experiment data to activate the embodied AI research copilot.'
    return sessions.at(-1).insight
  }, [sessions, telemetry])

  async function loadMetrics() {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/metrics`)
      if (!response.ok) throw new Error('Unable to load metrics from the API.')
      setData(await response.json())
      const architectureResponse = await fetch(`${API_URL}/platform/architecture`)
      if (architectureResponse.ok) setArchitecture(await architectureResponse.json())
    } catch (event) {
      setError(event.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleUpload(event) {
    const file = event.target.files?.[0]
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)
    setUploading(true)
    setError('')
    try {
      const response = await fetch(`${API_URL}/upload-csv`, {
        method: 'POST',
        body: formData,
      })
      if (!response.ok) {
        const body = await response.json()
        throw new Error(body.detail || 'CSV upload failed.')
      }
      await loadMetrics()
    } catch (event) {
      setError(event.message)
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  useEffect(() => {
    loadMetrics()
  }, [])

  useEffect(() => {
    const socket = new WebSocket(`${WS_URL}/ws/telemetry`)
    socket.onmessage = (event) => {
      setTelemetry(JSON.parse(event.data))
    }
    socket.onerror = () => {
      setError('Live telemetry stream is unavailable. The dashboard is showing stored session data.')
    }
    return () => socket.close()
  }, [])

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">HRI / VR evaluation framework</p>
          <h1>Embodied AI Research Operating Platform</h1>
        </div>
        <label className="upload-button">
          <input type="file" accept=".csv" onChange={handleUpload} disabled={uploading} />
          {uploading ? 'Uploading...' : 'Upload CSV'}
        </label>
      </header>

      {error && <div className="notice">{error}</div>}

      <section className="insight-band">
        <div>
          <span>AI Insight</span>
          <p>{topInsight}</p>
        </div>
        <button type="button" onClick={loadMetrics} disabled={loading}>
          Refresh
        </button>
      </section>

      {loading ? (
        <div className="loading">Loading telepresence metrics...</div>
      ) : (
        <Dashboard
          latest={latest}
          sessions={sessions}
          analytics={data?.analytics}
          architecture={architecture}
          telemetry={telemetry}
        />
      )}
    </main>
  )
}

export default App
