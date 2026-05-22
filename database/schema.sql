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
