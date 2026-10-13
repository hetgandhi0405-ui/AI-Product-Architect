-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: employees (Employee)
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
employee_code VARCHAR(50) UNIQUE NOT NULL NOT NULL,
name VARCHAR(255) NOT NULL NOT NULL,
department VARCHAR(100) NOT NULL NOT NULL,
designation VARCHAR(100) NOT NULL,
leave_balance INTEGER DEFAULT 24 NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_employees_user_id ON employees(user_id);

-- Table: attendance (Attendance)
CREATE TABLE IF NOT EXISTS attendance (
    id SERIAL PRIMARY KEY,
employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE NOT NULL,
date DATE NOT NULL NOT NULL,
clock_in TIMESTAMP WITH TIME ZONE NOT NULL,
clock_out TIMESTAMP WITH TIME ZONE,
status VARCHAR(50) DEFAULT 'present' NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_attendance_employee_id ON attendance(employee_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON attendance(date);
CREATE INDEX IF NOT EXISTS idx_attendance_status ON attendance(status);

-- Table: leave_requests (LeaveRequest)
CREATE TABLE IF NOT EXISTS leave_requests (
    id SERIAL PRIMARY KEY,
employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE NOT NULL,
leave_type VARCHAR(50) NOT NULL NOT NULL,
start_date DATE NOT NULL NOT NULL,
end_date DATE NOT NULL NOT NULL,
days_count INTEGER NOT NULL DEFAULT 5 NOT NULL,
reason TEXT NOT NULL NOT NULL,
status VARCHAR(50) DEFAULT 'pending' NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_leave_requests_employee_id ON leave_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(status);

-- Initial Seed Data for Employee Attendance Management
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
