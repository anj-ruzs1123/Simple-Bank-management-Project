# OOP Banking CLI

A learning-focused Python banking application with an interactive command-line interface and PostgreSQL persistence. It demonstrates object-oriented domain models, a service/repository architecture, exact decimal money handling, and atomic transfers.

> **Educational project:** This is a portfolio/learning demo, not production banking software. It has no customer authentication, authorization, deployment hardening, or regulatory controls. Do not use it to manage real money or sensitive financial data.

## Features

- Open standard, savings, and current accounts.
- Deposit, withdraw, transfer, and view balances and transaction statements.
- Apply interest to savings accounts.
- Freeze or reactivate accounts through the CLI; the service also supports closing eligible accounts.
- View a bank summary and total reserves.
- Persist account and transaction data in PostgreSQL.
- Use `Decimal` in Python and `NUMERIC` in PostgreSQL for monetary values.
- Record both sides of a transfer in one database transaction.

## How it works

```text
main.py (CLI)
    |
    v
BankService (banking use cases)
    |
    v
PostgresBankRepository (SQL, persistence, row mapping)
    |
    v
PostgreSQL
```

The CLI handles prompts and display. `BankService` coordinates operations. The repository reads and writes account and transaction rows, while the account models enforce account-specific rules. Database credentials are read from environment variables or a project-root `.env` file.

## Requirements

- Python 3.10 or newer
- A running PostgreSQL server
- PowerShell on Windows (commands below use PowerShell syntax)

## Quick start

Run these commands from the project root.

### 1. Create and activate a virtual environment

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

If PowerShell prevents activation, you can run the virtual environment's Python directly instead:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

If you activated the environment, install dependencies with:

```powershell
python -m pip install -r requirements.txt
```

### 2. Create a PostgreSQL role and database

Connect to PostgreSQL as an administrator using `psql` or SQL Shell and run these statements once. Replace the example password locally:

```sql
CREATE ROLE bank_app WITH LOGIN PASSWORD 'choose-a-local-password';
CREATE DATABASE oop_bank OWNER bank_app;
```

If the role already exists but PostgreSQL reports that it cannot log in, enable login:

```sql
ALTER ROLE bank_app WITH LOGIN;
```

Set or reset its password separately if needed:

```sql
ALTER ROLE bank_app WITH PASSWORD 'choose-a-local-password';
```

### 3. Configure the database connection

Copy `.env.example` to `.env` in the project root, then edit `.env` with the values for your local database:

```powershell
Copy-Item .env.example .env
```

Use these settings in `.env`:

```dotenv
PGHOST=localhost
PGPORT=5432
PGDATABASE=oop_bank
PGUSER=bank_app
PGPASSWORD=replace-with-your-local-password
```

The application loads `.env` when it opens a database connection. Keep `.env` private; it is ignored by Git. The checked-in `.env.example` contains placeholders only.

### 4. Create the database tables

```powershell
python -m src.repositories.setup_db
```

Expected result:

```text
PostgreSQL schema is ready.
```

This applies the SQL in `sql/schema.sql`. It is an explicit setup step; the CLI does not create or migrate the schema on startup.

### 5. Start the CLI

```powershell
python main.py
```

The menu lets you open accounts, make transactions, view statements, apply savings interest, manage account status, and view the bank summary. For a first persistence check, create an account, make a deposit, exit, start the CLI again, and look up the same account number.

## Tests

Run the unit and repository-mapping tests from the project root:

```powershell
python -m unittest discover -s tests -v
```

These tests are designed to run without a PostgreSQL connection. They cover domain operations, CLI behavior, and database-row-to-model mapping. They do **not** replace integration tests against a dedicated PostgreSQL test database.

## Project structure

```text
.
├── main.py                         # Interactive command-line interface
├── requirements.txt                # Python dependencies
├── sql/
│   └── schema.sql                  # PostgreSQL tables and constraints
├── src/
│   ├── models/                     # Account, transaction, and money rules
│   ├── repositories/               # PostgreSQL access and schema setup
│   └── services/                   # Banking use cases
└── tests/                          # Unit and repository mapping tests
```

## Design notes

- **Account types:** Standard and savings accounts enforce their minimum balance; current accounts may use their configured overdraft limit.
- **Money:** Inputs are converted to finite `Decimal` values and normalized to cents before model operations.
- **Transfers:** The repository locks both account rows and updates both balances and ledger entries in one transaction.
- **Statements:** Transaction records are stored separately and linked to their account by a foreign key.
- **Configuration:** `.env` is loaded by `python-dotenv`; do not commit database passwords or production credentials.

## Roadmap

- Add PostgreSQL integration tests for real create/read/update/close operations, transfers, and rollback behavior using an isolated test database.
- Expand automated test coverage and add continuous integration.
- Improve portfolio documentation as the project evolves.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.


