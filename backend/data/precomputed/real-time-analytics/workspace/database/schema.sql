-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: stream_sources (StreamSource)
CREATE TABLE IF NOT EXISTS stream_sources (
    id SERIAL PRIMARY KEY,
name VARCHAR(255) NOT NULL NOT NULL,
api_key_hash VARCHAR(255) NOT NULL NOT NULL,
status VARCHAR(50) DEFAULT 'active' NOT NULL,
events_per_sec INTEGER DEFAULT 1200 NOT NULL
);


-- Table: events (Event)
CREATE TABLE IF NOT EXISTS events (
    id SERIAL PRIMARY KEY,
source_id INTEGER REFERENCES stream_sources(id) ON DELETE CASCADE NOT NULL,
event_type VARCHAR(100) NOT NULL NOT NULL,
payload_json TEXT NOT NULL NOT NULL,
timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
ip_address VARCHAR(45) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_source_id ON events(source_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);

-- Table: metric_aggregations (MetricAggregation)
CREATE TABLE IF NOT EXISTS metric_aggregations (
    id SERIAL PRIMARY KEY,
metric_name VARCHAR(100) NOT NULL NOT NULL,
window_interval VARCHAR(20) NOT NULL NOT NULL,
count INTEGER NOT NULL NOT NULL,
sum_value NUMERIC(14, 2) NOT NULL,
avg_value NUMERIC(10, 2) NOT NULL,
window_end TIMESTAMP WITH TIME ZONE NOT NULL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_metric_aggregations_metric_name ON metric_aggregations(metric_name);
CREATE INDEX IF NOT EXISTS idx_metric_aggregations_window_end ON metric_aggregations(window_end);

-- Initial Seed Data for Real-Time Analytics Dashboard
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
