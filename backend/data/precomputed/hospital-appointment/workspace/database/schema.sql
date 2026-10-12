-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: doctors (Doctor)
CREATE TABLE IF NOT EXISTS doctors (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
name VARCHAR(255) NOT NULL NOT NULL,
specialty VARCHAR(100) NOT NULL NOT NULL,
license_number VARCHAR(50) UNIQUE NOT NULL NOT NULL,
room_number VARCHAR(30) NOT NULL,
is_available BOOLEAN DEFAULT TRUE NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_doctors_user_id ON doctors(user_id);
CREATE INDEX IF NOT EXISTS idx_doctors_specialty ON doctors(specialty);
CREATE INDEX IF NOT EXISTS idx_doctors_is_available ON doctors(is_available);

-- Table: patients (Patient)
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
name VARCHAR(255) NOT NULL NOT NULL,
blood_group VARCHAR(10) NOT NULL,
emergency_contact VARCHAR(100) NOT NULL,
date_of_birth VARCHAR(20) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_patients_user_id ON patients(user_id);

-- Table: appointments (Appointment)
CREATE TABLE IF NOT EXISTS appointments (
    id SERIAL PRIMARY KEY,
doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE NOT NULL,
patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE NOT NULL,
appointment_time TIMESTAMP WITH TIME ZONE NOT NULL NOT NULL,
reason TEXT NOT NULL NOT NULL,
status VARCHAR(50) DEFAULT 'scheduled' NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_appointments_doctor_id ON appointments(doctor_id);
CREATE INDEX IF NOT EXISTS idx_appointments_patient_id ON appointments(patient_id);
CREATE INDEX IF NOT EXISTS idx_appointments_appointment_time ON appointments(appointment_time);
CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);

-- Initial Seed Data for Hospital Appointment System
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
