"""
SQLite Database Schema Definitions
Defines tables for historical sales storage and upload history auditing.
"""

CREATE_SALES_TABLE = """
CREATE TABLE IF NOT EXISTS sales (
    order_id TEXT PRIMARY KEY,
    order_date TEXT NOT NULL,
    customer_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    brand TEXT NOT NULL,
    mrp REAL NOT NULL,
    discount_percent REAL NOT NULL,
    sale_price REAL NOT NULL,
    quantity INTEGER NOT NULL,
    revenue REAL NOT NULL,
    profit REAL NOT NULL,
    state TEXT NOT NULL,
    city TEXT NOT NULL,
    payment_method TEXT NOT NULL,
    rating REAL NOT NULL,
    delivery_days INTEGER NOT NULL,
    return_flag INTEGER NOT NULL,
    
    -- Engineered Features
    year INTEGER,
    month INTEGER,
    month_name TEXT,
    week INTEGER,
    day INTEGER,
    day_name TEXT,
    quarter INTEGER,
    revenue_per_item REAL,
    discount_amount REAL,
    profit_margin REAL,
    order_value REAL,
    is_returned INTEGER
);
"""

CREATE_UPLOAD_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS upload_history (
    upload_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    upload_timestamp TEXT NOT NULL,
    total_rows INTEGER NOT NULL,
    new_rows INTEGER NOT NULL,
    duplicate_rows INTEGER NOT NULL,
    invalid_rows INTEGER NOT NULL,
    status TEXT NOT NULL
);
"""

CREATE_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(order_date);",
    "CREATE INDEX IF NOT EXISTS idx_sales_category ON sales(category);",
    "CREATE INDEX IF NOT EXISTS idx_sales_brand ON sales(brand);",
    "CREATE INDEX IF NOT EXISTS idx_sales_state ON sales(state);",
    "CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_sales_year_month ON sales(year, month);",
    "CREATE INDEX IF NOT EXISTS idx_sales_return ON sales(return_flag);"
]
