-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: departments (Department)
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
name VARCHAR(100) NOT NULL NOT NULL,
sla_hours INTEGER DEFAULT 4 NOT NULL
);


-- Table: tickets (Ticket)
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
customer_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
assigned_agent_id INTEGER REFERENCES users(id),
department VARCHAR(100) DEFAULT 'General' NOT NULL,
subject VARCHAR(255) NOT NULL NOT NULL,
description TEXT NOT NULL NOT NULL,
priority VARCHAR(50) DEFAULT 'medium' NOT NULL,
status VARCHAR(50) DEFAULT 'open' NOT NULL,
sla_deadline TIMESTAMP WITH TIME ZONE NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_tickets_customer_id ON tickets(customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned_agent_id ON tickets(assigned_agent_id);
CREATE INDEX IF NOT EXISTS idx_tickets_department ON tickets(department);
CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority);
CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status);

-- Table: ticket_comments (TicketComment)
CREATE TABLE IF NOT EXISTS ticket_comments (
    id SERIAL PRIMARY KEY,
ticket_id INTEGER REFERENCES tickets(id) ON DELETE CASCADE NOT NULL,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
content TEXT NOT NULL NOT NULL,
is_internal BOOLEAN DEFAULT FALSE NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket_id ON ticket_comments(ticket_id);
CREATE INDEX IF NOT EXISTS idx_ticket_comments_user_id ON ticket_comments(user_id);

-- Initial Seed Data for Customer Support Ticket System
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
