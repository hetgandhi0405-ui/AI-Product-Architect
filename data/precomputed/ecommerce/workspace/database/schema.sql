-- System Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Table: products (Product)
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
name VARCHAR(255) NOT NULL NOT NULL,
sku VARCHAR(100) UNIQUE NOT NULL NOT NULL,
price NUMERIC(10, 2) NOT NULL NOT NULL,
stock_quantity INTEGER DEFAULT 0 NOT NULL,
category VARCHAR(100) DEFAULT 'Electronics' NOT NULL,
description TEXT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);
CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);

-- Table: orders (Order)
CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
user_id INTEGER REFERENCES users(id) ON DELETE CASCADE NOT NULL,
total_amount NUMERIC(10, 2) NOT NULL NOT NULL,
status VARCHAR(50) DEFAULT 'pending' NOT NULL,
shipping_address TEXT,
created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

-- Table: order_items (OrderItem)
CREATE TABLE IF NOT EXISTS order_items (
    id SERIAL PRIMARY KEY,
order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE NOT NULL,
product_id INTEGER REFERENCES products(id) NOT NULL,
quantity INTEGER NOT NULL DEFAULT 1 NOT NULL,
unit_price NUMERIC(10, 2) NOT NULL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);

-- Initial Seed Data for E-Commerce Platform
INSERT INTO users (email, hashed_password, role)
VALUES ('admin@cloud-architect.io', '$2b$12$KIXeWq1b3kF5q1tQZ9M8Me8iM.4W8qP4lC8f4Vq.f3H1b6E0O1L0e', 'administrator')
ON CONFLICT (email) DO NOTHING;
