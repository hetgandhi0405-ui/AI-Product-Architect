-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: courses (Course)
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
code VARCHAR(50) UNIQUE NOT NULL NOT NULL,
title VARCHAR(255) NOT NULL NOT NULL,
description TEXT,
instructor_id INTEGER REFERENCES users(id) NOT NULL,
credits INTEGER DEFAULT 4 NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_courses_code ON courses(code);
CREATE INDEX IF NOT EXISTS idx_courses_instructor_id ON courses(instructor_id);

-- Table: enrollments (Enrollment)
CREATE TABLE IF NOT EXISTS enrollments (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE NOT NULL,
enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
status VARCHAR(50) DEFAULT 'active' NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_enrollments_user_id ON enrollments(user_id);
CREATE INDEX IF NOT EXISTS idx_enrollments_course_id ON enrollments(course_id);

-- Table: assignments (Assignment)
CREATE TABLE IF NOT EXISTS assignments (
    id SERIAL PRIMARY KEY,
course_id INTEGER REFERENCES courses(id) ON DELETE CASCADE NOT NULL,
title VARCHAR(255) NOT NULL NOT NULL,
description TEXT NOT NULL,
due_date TIMESTAMP WITH TIME ZONE NOT NULL,
max_points INTEGER DEFAULT 100 NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_assignments_course_id ON assignments(course_id);

-- Table: submissions (Submission)
CREATE TABLE IF NOT EXISTS submissions (
    id SERIAL PRIMARY KEY,
assignment_id INTEGER REFERENCES assignments(id) ON DELETE CASCADE NOT NULL,
student_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
content TEXT NOT NULL NOT NULL,
grade NUMERIC(5, 2),
status VARCHAR(50) DEFAULT 'submitted' NOT NULL,
submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_submissions_assignment_id ON submissions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_submissions_student_id ON submissions(student_id);

-- Initial Seed Data for Student Learning Management System
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
