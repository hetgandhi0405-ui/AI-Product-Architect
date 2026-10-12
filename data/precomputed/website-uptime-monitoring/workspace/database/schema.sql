-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: monitored_urls (MonitoredUrl)
CREATE TABLE IF NOT EXISTS monitored_urls (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
name VARCHAR(255) NOT NULL NOT NULL,
url VARCHAR(500) NOT NULL NOT NULL,
check_interval_seconds INTEGER DEFAULT 60 NOT NULL,
expected_status_code INTEGER DEFAULT 200 NOT NULL,
timeout_seconds INTEGER DEFAULT 5 NOT NULL,
is_active BOOLEAN DEFAULT TRUE NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_monitored_urls_user_id ON monitored_urls(user_id);
CREATE INDEX IF NOT EXISTS idx_monitored_urls_url ON monitored_urls(url);
CREATE INDEX IF NOT EXISTS idx_monitored_urls_is_active ON monitored_urls(is_active);

-- Table: uptime_checks (UptimeCheck)
CREATE TABLE IF NOT EXISTS uptime_checks (
    id SERIAL PRIMARY KEY,
url_id INTEGER REFERENCES monitored_urls(id) ON DELETE CASCADE NOT NULL,
status_code INTEGER NOT NULL NOT NULL,
response_time_ms NUMERIC(10, 2) NOT NULL NOT NULL,
is_up BOOLEAN NOT NULL NOT NULL,
checked_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_uptime_checks_url_id ON uptime_checks(url_id);
CREATE INDEX IF NOT EXISTS idx_uptime_checks_is_up ON uptime_checks(is_up);
CREATE INDEX IF NOT EXISTS idx_uptime_checks_checked_at ON uptime_checks(checked_at);

-- Table: incidents (Incident)
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
url_id INTEGER REFERENCES monitored_urls(id) ON DELETE CASCADE NOT NULL,
started_at TIMESTAMP WITH TIME ZONE NOT NULL NOT NULL,
resolved_at TIMESTAMP WITH TIME ZONE,
status VARCHAR(50) DEFAULT 'ongoing' NOT NULL,
root_cause TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_incidents_url_id ON incidents(url_id);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents(status);

-- Initial Seed Data for Website Uptime Monitoring
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
