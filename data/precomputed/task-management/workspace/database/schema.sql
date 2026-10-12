-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: tasks (Task)
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
title VARCHAR(255) NOT NULL NOT NULL,
description TEXT,
priority VARCHAR(50) DEFAULT 'medium' NOT NULL,
status VARCHAR(50) DEFAULT 'pending' NOT NULL,
due_date TIMESTAMP WITH TIME ZONE,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tasks_user_id ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);

-- Table: categories (Category)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL NOT NULL,
color VARCHAR(30) DEFAULT '#3b82f6' NOT NULL
);


-- Initial Seed Data for Task Management System
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
