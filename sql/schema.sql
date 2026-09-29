CREATE TABLE IF NOT EXISTS accounts (
    account_number TEXT PRIMARY KEY,
    holder_name TEXT NOT NULL CHECK (length(trim(holder_name)) > 0),
    account_type TEXT NOT NULL
        CHECK (account_type IN ('standard', 'savings', 'current')),
    balance NUMERIC(18, 2) NOT NULL,
    minimum_balance NUMERIC(18, 2) NOT NULL CHECK (minimum_balance >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_closed BOOLEAN NOT NULL DEFAULT FALSE,
    interest_rate NUMERIC(8, 6),
    overdraft_limit NUMERIC(18, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT account_type_settings_check CHECK (
        (account_type = 'standard' AND interest_rate IS NULL AND overdraft_limit IS NULL)
        OR
        (account_type = 'savings' AND interest_rate IS NOT NULL
            AND interest_rate >= 0 AND overdraft_limit IS NULL)
        OR
        (account_type = 'current' AND interest_rate IS NULL
            AND overdraft_limit IS NOT NULL AND overdraft_limit >= 0)
    ),
    CONSTRAINT account_balance_floor_check CHECK (
        (account_type = 'current' AND balance >= -overdraft_limit)
        OR
        (account_type IN ('standard', 'savings') AND balance >= 0)
    )
);

ALTER TABLE accounts
    ADD COLUMN IF NOT EXISTS is_closed BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id TEXT PRIMARY KEY,
    account_number TEXT NOT NULL
        REFERENCES accounts(account_number) ON DELETE RESTRICT,
    occurred_at TIMESTAMPTZ NOT NULL,
    transaction_type TEXT NOT NULL
        CHECK (transaction_type IN (
            'DEPOSIT', 'WITHDRAWAL', 'TRANSFER_IN', 'TRANSFER_OUT', 'INTEREST'
        )),
    amount NUMERIC(18, 2) NOT NULL CHECK (amount > 0),
    balance_after NUMERIC(18, 2) NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS transactions_account_time_idx
    ON transactions (account_number, occurred_at, transaction_id);