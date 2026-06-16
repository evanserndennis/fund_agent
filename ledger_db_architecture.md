# AI Fund Admin — Database Design

A reference for the data model behind an agentic fund administration system that reads
the general ledger, determines when capital calls or distributions are required (and for
how much), allocates them across investors, and generates the resulting notices.

Assumed fund type: a **closed-end private fund** (PE / VC / private credit / real estate)
with limited partners who make commitments drawn down over time. Hedge / open-end funds
don't do capital calls, so the model is built for the closed-end case.

---

## 1. Core design principles

The single most important decision: treat the **general ledger as an immutable,
append-only record of what actually happened with money**, and build a separate
**operational layer** on top that manages the *process* of calling and distributing
capital. The agent reads from the ledger (plus cash and portfolio state) to decide what's
needed, proposes a call or distribution in the operational layer, and only once that's
approved and executed do the corresponding entries post to the ledger.

Three principles fall out of this and govern the whole schema:

1. **Immutability of financial records.** Never `UPDATE` a posted journal entry or a
   contribution. Corrections are *reversing entries*, not edits. Balances are *derived*
   from transactions, not stored as mutable fields (or stored only as periodic snapshots
   that can always be rebuilt). This is what makes the system auditable and lets you
   reconstruct fund state as of any date.

2. **Allocation snapshots.** Each investor's ownership percentage changes as new investors
   join at later closes. At the moment a call is issued, *freeze* the allocation basis used
   — don't recompute it later from current commitments.

3. **The agent proposes, humans dispose.** Model an explicit
   `draft → proposed → approved → issued` lifecycle, and persist the agent's reasoning next
   to each proposal. The agent should never move money autonomously, and the "why did it
   decide this" trail is half of what the demonstrator is showing off.

**Tech note:** Postgres is the natural fit — strong relational integrity for the
accounting core, `NUMERIC`/`DECIMAL` for money (never floating point), `JSONB` for the
agent's flexible rationale and for side-letter / config terms that vary per investor, and
good support for the temporal queries this design leans on. Store a currency code alongside
every monetary amount.

---

## 2. The six layers

| Layer | Purpose | Tables |
|-------|---------|--------|
| 1. Master data | Who the fund and investors are, and who committed what | `funds`, `investors`, `closings`, `commitments` |
| 2. General ledger | Immutable source of truth for money movement | `chart_of_accounts`, `journal_entries`, `journal_lines` |
| 3. Portfolio | What drives cash needs and proceeds | `investments` |
| 4. Capital activity | The calls/distributions the agent generates | `capital_calls`, `call_allocations`, `distributions`, `distribution_allocations` |
| 5. Documents | Templates and rendered investor notices | `document_templates`, `generated_documents` |
| 6. Agent & audit | Decision provenance, approvals, audit trail | `agent_runs`, `agent_decisions`, `approvals`, `audit_log` |

---

## 3. Table-by-table schema

Column lists below are illustrative starting points, not exhaustive. `PK` = primary key,
`FK` = foreign key. Use `UUID` keys, `NUMERIC` for all money, `TIMESTAMPTZ` for times.

### Layer 1 — Master data

**`funds`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `name` | TEXT | |
| `base_currency` | CHAR(3) | ISO currency code |
| `vintage_year` | INT | |
| `fund_term` | INT | Years |
| `mgmt_fee_rate` | NUMERIC | e.g. 0.0200 |
| `hurdle_rate` | NUMERIC | Preferred return |
| `carry_rate` | NUMERIC | GP carried interest |
| `status` | TEXT | fundraising / investing / harvesting / wound_down |

**`investors`** — the LPs, plus the GP entity itself

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `legal_name` | TEXT | |
| `type` | TEXT | individual / institution / GP |
| `tax_id` | TEXT | Encrypt at rest |
| `kyc_status` | TEXT | |
| `banking_ref` | JSONB | Or FK to a separate banking table |
| `contact` | JSONB | |

**`closings`** — funds raise across multiple closes; this drives equalization

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `fund_id` | UUID FK | |
| `closing_number` | INT | 1 = first close |
| `closing_date` | DATE | |

**`commitments`** — the investor ↔ fund link carrying the committed amount

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `fund_id` | UUID FK | |
| `investor_id` | UUID FK | |
| `closing_id` | UUID FK | Which close they came in at |
| `commitment_amount` | NUMERIC | |
| `commitment_date` | DATE | |

### Layer 2 — General ledger

**`chart_of_accounts`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `account_code` | TEXT | |
| `account_name` | TEXT | |
| `account_type` | TEXT | asset / liability / equity / income / expense |
| `normal_balance` | TEXT | debit / credit |

**`journal_entries`** — the header

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `fund_id` | UUID FK | |
| `entry_date` | DATE | |
| `description` | TEXT | |
| `source` | TEXT | manual / system / agent |
| `posted` | BOOLEAN | Once true, never edit |
| `reversal_of` | UUID FK | Self-ref for correcting entries |

**`journal_lines`** — the debit/credit detail

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `entry_id` | UUID FK | |
| `account_id` | UUID FK | |
| `investor_id` | UUID FK | **Nullable** — sub-ledger dimension for partner-level capital accounts |
| `debit` | NUMERIC | |
| `credit` | NUMERIC | |
| `memo` | TEXT | |

> The optional `investor_id` on each line is what lets you carry per-LP capital accounts
> inside the same ledger. Don't store each LP's contributed / distributed / unfunded / NAV
> as editable columns — *derive* them from the ledger and capital activity, snapshotting per
> accounting period if you want fast reads.

### Layer 3 — Portfolio

**`investments`** — what generates the cash needs and proceeds

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `fund_id` | UUID FK | |
| `company_name` | TEXT | |
| `invested_amount` | NUMERIC | Drives calls |
| `current_value` | NUMERIC | |
| `realized_proceeds` | NUMERIC | Drives distributions |
| `status` | TEXT | active / partially_realized / realized / written_off |

### Layer 4 — Capital activity

**`capital_calls`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `fund_id` | UUID FK | |
| `agent_run_id` | UUID FK | Which agent run proposed it |
| `call_number` | INT | Unique with `fund_id` — idempotency |
| `call_date` | DATE | |
| `due_date` | DATE | |
| `total_amount` | NUMERIC | |
| `purpose` | TEXT | investment / expense / fee |
| `status` | TEXT | draft / proposed / approved / issued / funded |

**`call_allocations`** — one row per investor

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `call_id` | UUID FK | |
| `investor_id` | UUID FK | |
| `amount` | NUMERIC | |
| `basis_pct` | NUMERIC | **Frozen** at issuance, not joined live |
| `unfunded_before` | NUMERIC | |
| `unfunded_after` | NUMERIC | |
| `status` | TEXT | |

**`distributions`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `fund_id` | UUID FK | |
| `agent_run_id` | UUID FK | |
| `distribution_number` | INT | Unique with `fund_id` |
| `distribution_date` | DATE | |
| `total_amount` | NUMERIC | |
| `type` | TEXT | return_of_capital / income / gain |
| `recallable` | BOOLEAN | If true, flows back to unfunded commitment |
| `status` | TEXT | draft / proposed / approved / issued |

**`distribution_allocations`** — one row per investor, with waterfall breakdown

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `distribution_id` | UUID FK | |
| `investor_id` | UUID FK | |
| `return_of_capital` | NUMERIC | |
| `pref_return` | NUMERIC | Preferred / hurdle portion |
| `profit` | NUMERIC | |
| `gp_carry` | NUMERIC | Carried interest split |
| `total` | NUMERIC | |

### Layer 5 — Documents

**`document_templates`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `doc_type` | TEXT | call_notice / distribution_notice |
| `version` | INT | |
| `body` | TEXT | Template content / path |

**`generated_documents`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `template_id` | UUID FK | |
| `doc_type` | TEXT | |
| `allocation_id` | UUID | Points to a call or distribution allocation row |
| `investor_id` | UUID FK | |
| `file_path` | TEXT | |
| `generated_at` | TIMESTAMPTZ | |
| `status` | TEXT | draft / sent |

### Layer 6 — Agent & audit

**`agent_runs`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `trigger` | TEXT | scheduled / manual / event |
| `started_at` | TIMESTAMPTZ | |
| `inputs_snapshot` | JSONB | Balances and obligations the agent reasoned over |
| `rationale` | JSONB | Why it proposed what it did |
| `confidence` | NUMERIC | |
| `model_version` | TEXT | |

**`agent_decisions`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `run_id` | UUID FK | |
| `decision_type` | TEXT | call / distribution / no_action |
| `supporting_data` | JSONB | |
| `requires_approval` | BOOLEAN | |

**`approvals`**

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `entity_type` | TEXT | capital_call / distribution |
| `entity_id` | UUID | |
| `approver` | TEXT | |
| `decision` | TEXT | approved / rejected |
| `comments` | TEXT | |
| `decided_at` | TIMESTAMPTZ | |

**`audit_log`** — append-only record of every change

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID PK | |
| `actor` | TEXT | user / agent / system |
| `action` | TEXT | |
| `entity_type` | TEXT | |
| `entity_id` | UUID | |
| `before` | JSONB | |
| `after` | JSONB | |
| `at` | TIMESTAMPTZ | |

---

## 4. Design considerations

- **Exact-decimal money, never floats.** Use `NUMERIC`/`DECIMAL`. Float rounding errors in a
  system that must tie out to the penny will undermine the demonstrator's credibility.

- **Persist the determination logic's inputs, not just its output.** The two decisions are
  roughly: a *call* equals forecasted obligations (deals to fund, expenses, fees due) minus
  available cash above a reserve; a *distribution* equals realizable cash above the reserve,
  sourced from proceeds. Store the snapshot of balances and obligations in
  `agent_runs.inputs_snapshot` so a human can see why it landed where it did.

- **Snapshot the allocation basis at issuance.** `call_allocations.basis_pct` is the frozen
  value used that day. The allocation math has real-world wrinkles worth at least stubbing:
  investors *excused* from a particular investment, *equalization / true-up* charged to LPs
  who join at a later close, *recallable* distributions flowing back into unfunded commitment,
  and *management fee offsets* netted against calls.

- **Idempotency.** A unique constraint on `(fund_id, call_number)` plus the status machine
  prevents the agent from issuing the same call twice if it runs again.

- **Append-only ledger at the application layer.** No edits to posted entries; corrections
  are reversing entries (`journal_entries.reversal_of`). Combined with immutable
  contribution/distribution records, this gives point-in-time reconstruction — answering
  "what did this LP's capital account look like on March 31" by replaying transactions.

---

## 5. Open forks that change the design

1. **Consume vs. produce the GL.** Is the app *reading* a general ledger from an existing
   accounting system, or *is it* the system of record that also produces the GL? If reading,
   layers 1–2 become an integration/sync problem and you own the operational layers. If
   producing, you build double-entry accounting from scratch — more work, but a cleaner,
   self-contained demo.

2. **Fund strategy.** PE buyout, VC, private credit, and real estate all do calls and
   distributions, but the distribution waterfall and allocation nuances differ. For a
   demonstrator, model one strategy cleanly and gesture at the rest.
