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

CREATE TABLE adaptive_actions (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    action_name VARCHAR(160) NOT NULL,
    trigger_reason TEXT,
    applied BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE embodied_consciousness_states (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    awareness FLOAT NOT NULL,
    attention FLOAT NOT NULL,
    control_confidence FLOAT NOT NULL,
    adaptation FLOAT NOT NULL,
    presence_continuity FLOAT NOT NULL,
    state VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE human_digital_twins (
    id SERIAL PRIMARY KEY,
    participant_id INT REFERENCES participants(id),
    physiological_baseline JSONB,
    adaptation_profile VARCHAR(120),
    embodiment_fingerprint JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE embodied_memory_events (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    failure_pattern VARCHAR(160),
    recovery_strategy VARCHAR(160),
    memory_strength FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reality_sync_states (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    physical_robot_sync FLOAT,
    vr_world_sync FLOAT,
    body_state_sync FLOAT,
    physiological_stream_sync FLOAT,
    unified_reality_score FLOAT,
    orchestration_state VARCHAR(80),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE autonomous_scientist_outputs (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    observed TEXT,
    hypothesis TEXT,
    suggested_experiment TEXT,
    analysis_plan JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE neural_presence_states (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    presence_transmission FLOAT NOT NULL,
    intention_clarity FLOAT,
    emotional_bandwidth FLOAT,
    embodiment_signal FLOAT,
    state VARCHAR(80),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE persistent_digital_self_profiles (
    id SERIAL PRIMARY KEY,
    participant_id INT REFERENCES participants(id),
    continuity_score FLOAT NOT NULL,
    embodiment_preferences JSONB,
    memory_aware_summary TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ai_companion_interventions (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    tone VARCHAR(80),
    message TEXT NOT NULL,
    interventions JSONB,
    emotional_state_estimate VARCHAR(80),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sensory_presence_states (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    haptic_fidelity FLOAT,
    visual_fidelity FLOAT,
    spatial_audio_fidelity FLOAT,
    tactile_presence FLOAT,
    full_sensory_presence FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE shared_reality_spaces (
    id SERIAL PRIMARY KEY,
    session_id INT REFERENCES sessions(id),
    collaboration_trust FLOAT,
    team_cognitive_load FLOAT,
    social_presence_sync FLOAT,
    space_state VARCHAR(80),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
