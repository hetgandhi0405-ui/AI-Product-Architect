-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: categories (Category)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
name VARCHAR(100) NOT NULL NOT NULL,
type VARCHAR(50) DEFAULT 'expense' NOT NULL,
color VARCHAR(30) DEFAULT '#10b981' NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_categories_user_id ON categories(user_id);

-- Table: transactions (Transaction)
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
category_id INTEGER REFERENCES categories(id) NOT NULL,
amount NUMERIC(12, 2) NOT NULL NOT NULL,
transaction_type VARCHAR(50) NOT NULL NOT NULL,
description VARCHAR(255) NOT NULL,
date TIMESTAMP WITH TIME ZONE NOT NULL NOT NULL,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_category_id ON transactions(category_id);
CREATE INDEX IF NOT EXISTS idx_transactions_transaction_type ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);

-- Table: budgets (Budget)
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE NOT NULL,
monthly_limit NUMERIC(12, 2) NOT NULL NOT NULL,
current_spent NUMERIC(12, 2) DEFAULT 0.0 NOT NULL,
month_year VARCHAR(20) NOT NULL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_budgets_category_id ON budgets(category_id);

-- Initial Seed Data for Personal Finance Tracker
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
