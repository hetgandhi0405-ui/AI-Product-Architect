-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: devices (Device)
CREATE TABLE IF NOT EXISTS devices (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
name VARCHAR(255) NOT NULL NOT NULL,
device_type VARCHAR(100) NOT NULL NOT NULL,
room VARCHAR(100) NOT NULL,
ip_address VARCHAR(45) NOT NULL,
status VARCHAR(50) DEFAULT 'online' NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_devices_user_id ON devices(user_id);
CREATE INDEX IF NOT EXISTS idx_devices_device_type ON devices(device_type);
CREATE INDEX IF NOT EXISTS idx_devices_status ON devices(status);

-- Table: sensor_readings (SensorReading)
CREATE TABLE IF NOT EXISTS sensor_readings (
    id SERIAL PRIMARY KEY,
device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE NOT NULL,
metric VARCHAR(100) NOT NULL NOT NULL,
value NUMERIC(10, 2) NOT NULL NOT NULL,
unit VARCHAR(20) NOT NULL NOT NULL,
timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_device_id ON sensor_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_metric ON sensor_readings(metric);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(timestamp);

-- Table: alert_rules (AlertRule)
CREATE TABLE IF NOT EXISTS alert_rules (
    id SERIAL PRIMARY KEY,
device_id INTEGER REFERENCES devices(id) ON DELETE CASCADE NOT NULL,
metric VARCHAR(100) NOT NULL NOT NULL,
condition VARCHAR(20) NOT NULL NOT NULL,
threshold NUMERIC(10, 2) NOT NULL NOT NULL,
is_active BOOLEAN DEFAULT TRUE NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_alert_rules_device_id ON alert_rules(device_id);

-- Initial Seed Data for Smart Home Dashboard
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
