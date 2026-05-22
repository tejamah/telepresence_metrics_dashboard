CREATE TABLE participants (
    id SERIAL PRIMARY KEY,
    participant_code VARCHAR(50) UNIQUE NOT NULL,
    age INT,
    gender VARCHAR(50),
    prior_vr_experience VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    participant_id INT REFERENCES participants(id),
    task_type VARCHAR(120) NOT NULL,
    setup VARCHAR(160) NOT NULL,
    session_time TIMESTAMP NOT NULL,
    notes TEXT
);

CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    category VARCHAR(60) NOT NULL,
    score FLOAT NOT NULL,
    level VARCHAR(20) NOT NULL
);

CREATE TABLE submetrics (
    id SERIAL PRIMARY KEY,
    metric_id INT REFERENCES metrics(id),
    name VARCHAR(80) NOT NULL,
    raw_value FLOAT NOT NULL,
    normalized_score FLOAT NOT NULL,
    unit VARCHAR(30)
);

CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    sensor_type VARCHAR(80) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(30)
);

CREATE TABLE questionnaire_responses (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    instrument VARCHAR(80) NOT NULL,
    question_key VARCHAR(80) NOT NULL,
    response_value FLOAT NOT NULL
);

CREATE TABLE system_logs (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    timestamp TIMESTAMP NOT NULL,
    latency_ms FLOAT,
    fps FLOAT,
    packet_loss_percent FLOAT,
    event_label VARCHAR(120)
);

CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    overall_score FLOAT NOT NULL,
    overall_level VARCHAR(20) NOT NULL,
    insight TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE telemetry_streams (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    source VARCHAR(80) NOT NULL,
    stream_type VARCHAR(80) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    payload JSONB NOT NULL
);

CREATE TABLE risk_events (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    risk_type VARCHAR(120) NOT NULL,
    severity VARCHAR(30) NOT NULL,
    detail TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE digital_twin_snapshots (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    robot_pose JSONB,
    user_pose JSONB,
    environment_state JSONB,
    timestamp TIMESTAMP NOT NULL
);

CREATE TABLE vector_documents (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    document_type VARCHAR(80) NOT NULL,
    content TEXT NOT NULL,
    embedding_id VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE model_predictions (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    model_name VARCHAR(120) NOT NULL,
    prediction_type VARCHAR(120) NOT NULL,
    prediction_value FLOAT NOT NULL,
    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cognitive_state_events (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    cognitive_stability FLOAT NOT NULL,
    collapse_risk_score FLOAT NOT NULL,
    attention_drift FLOAT,
    stress_escalation VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE explainability_factors (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    prediction_id INT REFERENCES model_predictions(id),
    factor_name VARCHAR(120) NOT NULL,
    factor_value FLOAT,
    impact FLOAT NOT NULL,
    detail TEXT NOT NULL
);

CREATE TABLE ai_sbom_components (
    id SERIAL PRIMARY KEY,
    component_name VARCHAR(160) NOT NULL,
    component_type VARCHAR(80) NOT NULL,
    baseline_reliability FLOAT NOT NULL,
    runtime_reliability FLOAT,
    status VARCHAR(40),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE adaptive_actions (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    action_name VARCHAR(160) NOT NULL,
    trigger_reason TEXT,
    applied BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
