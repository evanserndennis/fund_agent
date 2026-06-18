from db_connection import get_db_connection

CREATE_SCHEMA_SQL = """

-- ── Layer 1: Master data ─────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS funds (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    base_currency   CHAR(3) NOT NULL,
    vintage_year    INT,
    fund_term       INT,
    mgmt_fee_rate   NUMERIC,
    hurdle_rate     NUMERIC,
    carry_rate      NUMERIC,
    status          TEXT CHECK (status IN ('fundraising', 'investing', 'harvesting', 'wound_down'))
);

CREATE TABLE IF NOT EXISTS investors (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_name   TEXT NOT NULL,
    type         TEXT CHECK (type IN ('individual', 'institution', 'GP')),
    tax_id       TEXT,
    kyc_status   TEXT,
    banking_ref  JSONB,
    contact      JSONB
);

CREATE TABLE IF NOT EXISTS closings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fund_id         UUID NOT NULL REFERENCES funds(id),
    closing_number  INT NOT NULL,
    closing_date    DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS commitments (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fund_id           UUID NOT NULL REFERENCES funds(id),
    investor_id       UUID NOT NULL REFERENCES investors(id),
    closing_id        UUID REFERENCES closings(id),
    commitment_amount NUMERIC NOT NULL,
    commitment_date   DATE
);

-- ── Layer 2: General ledger ──────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS chart_of_accounts (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_code   TEXT NOT NULL UNIQUE,
    account_name   TEXT NOT NULL,
    account_type   TEXT CHECK (account_type IN ('asset', 'liability', 'equity', 'income', 'expense')),
    normal_balance TEXT CHECK (normal_balance IN ('debit', 'credit'))
);

CREATE TABLE IF NOT EXISTS journal_entries (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fund_id      UUID NOT NULL REFERENCES funds(id),
    entry_date   DATE NOT NULL,
    description  TEXT,
    source       TEXT CHECK (source IN ('manual', 'system', 'agent')),
    posted       BOOLEAN NOT NULL DEFAULT FALSE,
    reversal_of  UUID REFERENCES journal_entries(id)
);

CREATE TABLE IF NOT EXISTS journal_lines (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entry_id    UUID NOT NULL REFERENCES journal_entries(id),
    account_id  UUID NOT NULL REFERENCES chart_of_accounts(id),
    investor_id UUID REFERENCES investors(id),
    debit       NUMERIC NOT NULL DEFAULT 0,
    credit      NUMERIC NOT NULL DEFAULT 0,
    memo        TEXT
);

-- ── Layer 3: Portfolio ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS investments (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fund_id           UUID NOT NULL REFERENCES funds(id),
    company_name      TEXT NOT NULL,
    invested_amount   NUMERIC NOT NULL DEFAULT 0,
    current_value     NUMERIC,
    realized_proceeds NUMERIC NOT NULL DEFAULT 0,
    status            TEXT CHECK (status IN ('active', 'partially_realized', 'realized', 'written_off'))
);

-- ── Layer 6 (partial): Agent runs — created here because capital activity FKs it ──

CREATE TABLE IF NOT EXISTS agent_runs (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trigger          TEXT CHECK (trigger IN ('scheduled', 'manual', 'event')),
    started_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    inputs_snapshot  JSONB,
    rationale        JSONB,
    confidence       NUMERIC,
    model_version    TEXT
);

-- ── Layer 4: Capital activity ────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS capital_calls (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fund_id       UUID NOT NULL REFERENCES funds(id),
    agent_run_id  UUID REFERENCES agent_runs(id),
    call_number   INT NOT NULL,
    call_date     DATE NOT NULL,
    due_date      DATE,
    total_amount  NUMERIC NOT NULL,
    purpose       TEXT CHECK (purpose IN ('investment', 'expense', 'fee')),
    status        TEXT CHECK (status IN ('draft', 'proposed', 'approved', 'issued', 'funded')),
    UNIQUE (fund_id, call_number)
);

CREATE TABLE IF NOT EXISTS call_allocations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    call_id         UUID NOT NULL REFERENCES capital_calls(id),
    investor_id     UUID NOT NULL REFERENCES investors(id),
    amount          NUMERIC NOT NULL,
    basis_pct       NUMERIC NOT NULL,
    unfunded_before NUMERIC,
    unfunded_after  NUMERIC,
    status          TEXT
);

CREATE TABLE IF NOT EXISTS distributions (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fund_id             UUID NOT NULL REFERENCES funds(id),
    agent_run_id        UUID REFERENCES agent_runs(id),
    distribution_number INT NOT NULL,
    distribution_date   DATE NOT NULL,
    total_amount        NUMERIC NOT NULL,
    type                TEXT CHECK (type IN ('return_of_capital', 'income', 'gain')),
    recallable          BOOLEAN NOT NULL DEFAULT FALSE,
    status              TEXT CHECK (status IN ('draft', 'proposed', 'approved', 'issued')),
    UNIQUE (fund_id, distribution_number)
);

CREATE TABLE IF NOT EXISTS distribution_allocations (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    distribution_id   UUID NOT NULL REFERENCES distributions(id),
    investor_id       UUID NOT NULL REFERENCES investors(id),
    return_of_capital NUMERIC NOT NULL DEFAULT 0,
    pref_return       NUMERIC NOT NULL DEFAULT 0,
    profit            NUMERIC NOT NULL DEFAULT 0,
    gp_carry          NUMERIC NOT NULL DEFAULT 0,
    total             NUMERIC NOT NULL DEFAULT 0
);

-- ── Layer 5: Documents ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS document_templates (
    id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    doc_type TEXT CHECK (doc_type IN ('call_notice', 'distribution_notice')),
    version  INT NOT NULL,
    body     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS generated_documents (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id   UUID REFERENCES document_templates(id),
    doc_type      TEXT,
    allocation_id UUID,
    investor_id   UUID NOT NULL REFERENCES investors(id),
    file_path     TEXT,
    generated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status        TEXT CHECK (status IN ('draft', 'sent'))
);

-- ── Layer 6 (remainder): Agent decisions, approvals, audit ───────────────────

CREATE TABLE IF NOT EXISTS agent_decisions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id            UUID NOT NULL REFERENCES agent_runs(id),
    decision_type     TEXT CHECK (decision_type IN ('call', 'distribution', 'no_action')),
    supporting_data   JSONB,
    requires_approval BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS approvals (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT CHECK (entity_type IN ('capital_call', 'distribution')),
    entity_id   UUID NOT NULL,
    approver    TEXT NOT NULL,
    decision    TEXT CHECK (decision IN ('approved', 'rejected')),
    comments    TEXT,
    decided_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS audit_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor       TEXT NOT NULL,
    action      TEXT NOT NULL,
    entity_type TEXT,
    entity_id   UUID,
    before      JSONB,
    after       JSONB,
    at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

with get_db_connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute(CREATE_SCHEMA_SQL)
    conn.commit()

print("Schema initialized: 18 tables created.")
