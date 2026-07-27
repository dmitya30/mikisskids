PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tranid TEXT NOT NULL UNIQUE,
    received_at TEXT NOT NULL,
    formid TEXT,
    tilda_order_id TEXT,
    product_text TEXT,
    amount_text TEXT,
    customer_name TEXT,
    phone TEXT,
    email TEXT,
    city TEXT,
    comment TEXT,
    source_url TEXT,
    status TEXT NOT NULL,
    raw_payload_json TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_orders_received_at
    ON orders(received_at);

CREATE INDEX IF NOT EXISTS idx_orders_email
    ON orders(email);
