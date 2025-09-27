CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,       -- unique transaction identifier
    email_id VARCHAR(255) NOT NULL,          -- identifies the person
    amount NUMERIC(12,2) NOT NULL,           -- transaction amount with 2 decimal places
    currency VARCHAR(10) NOT NULL DEFAULT 'USD', -- ISO 4217 currency code
    transaction_type VARCHAR(50) NOT NULL,   -- e.g., 'debit', 'credit', 'refund'
    category VARCHAR(50) NOT NULL,           -- e.g., 'food', 'clothes', 'shopping', 'other'
    description TEXT,                        -- optional description
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, -- timestamp

    -- Constraint for valid email format
    CONSTRAINT email_format CHECK (email_id ~* 
        '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),

    -- Optional: Restrict allowed categories
    CONSTRAINT valid_category CHECK (
        category IN ('food', 'clothes', 'shopping', 'entertainment', 'travel', 'other')
    )
);
