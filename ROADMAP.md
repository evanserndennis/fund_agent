# Roadmap

Tracks milestones for the AI fund administration system described in
[`src/fund_agent/db/SCHEMA.md`](src/fund_agent/db/SCHEMA.md). Checked items are built and
seeded; unchecked items are what's left, roughly in dependency order.

---

## Milestone 0 — Data layer

- [x] Schema DDL for all 18 tables across the six layers (`db/db_initialization.py`)
- [x] Pydantic models for every table (`models/`)
- [x] Modular seeders for all six layers (`db/db_seeder/`)
- [x] DB connection + init verification (`db_connection.py`, `db_init_verification.py`)
- [x] Packaging (`pyproject.toml`, editable install, pinned `requirements.txt`)

## Milestone 1 — Foundation helpers

Shared primitives the services below all depend on — build once, use everywhere, rather
than letting each service reinvent them.

- [x] Decimal-safe money helpers (`services/money.py`: `money()`, `allocate_pro_rata()`)
- [x] Reserve policy (`services/reserve.py`: fixed $15,000 default, `FUND_RESERVE_AMOUNT`
      env override — no per-account modeling, matches how the schema tracks cash)
- [x] Trial balance helper (`services/trial_balance.py`: `trial_balance()` replays all
      journal lines up to a date, held or posted; backs both balance lookups and the
      "what did this LP's account look like on X" case — held entries count because a
      future-dated, not-yet-cash-confirmed call/distribution is still real recorded
      activity, just not locked yet)

## Milestone 2 — Read-only state services

- [x] `services/ledger.py` — `cash_balance()`: resolves the `"1001"` cash account code to
      its id and reads the balance off `trial_balance()`
- [ ] `services/ledger.py` — per-investor capital account (contributed / distributed /
      unfunded / NAV): `trial_balance()` called with `investor_id` set

`services/portfolio.py` was cut — see note below.

## Milestone 3 — Determination engine

- [ ] `services/determination.py` — reads the ledger via `trial_balance()` with a
      forward-dated `as_of` (e.g. two weeks out) to see held/future-dated entries already
      recorded for upcoming calls/distributions; if it isn't on the ledger, it isn't
      considered — no separate obligations source. Distribution sizing is cash above
      reserve; `distributions.recallable` is the correction mechanism if a distribution
      turns out to be needed back, so sizing doesn't need to prove realized-proceeds
      provenance up front. Produces the `inputs_snapshot` + `rationale` payloads for
      `agent_runs`

## Milestone 4 — Allocation engines

- [ ] `services/call_allocation.py` — pro-rata split, frozen `basis_pct`, equalization/
      true-up for later closes, excused-investor handling, management fee offsets
- [ ] `services/waterfall.py` — return of capital, preferred/hurdle return, profit split,
      GP carry, recallable-distribution handling (feeds back into unfunded commitment)

## Milestone 5 — Lifecycle services

- [ ] `services/capital_calls.py` — `draft → proposed → approved → issued → funded` state
      machine, orchestrates determination + allocation. `call_number` assigned inline via
      `INSERT ... SELECT COALESCE(MAX(call_number), 0) + 1 ... WHERE fund_id = ...` in the
      same transaction as the insert; the `(fund_id, call_number)` UNIQUE constraint is the
      backstop against a race, not a separate helper
- [ ] `services/distributions.py` — `draft → proposed → approved → issued`, orchestrates
      determination + waterfall; `distribution_number` assigned the same way

## Milestone 6 — Agent & governance

- [ ] `services/agent.py` — creates `agent_runs` / `agent_decisions`, ties decisions back
      to the calls/distributions they produced
- [ ] `services/approvals.py` — records approvals, gates `proposed → approved`; no
      autonomous execution path

## Milestone 7 — Ledger posting

- [ ] `services/posting.py` — writes `journal_entries` + `journal_lines` once a call/
      distribution is issued/funded; corrections are reversing entries, never edits to
      posted rows

## Milestone 8 — Documents

- [ ] `services/documents.py` — renders `document_templates` against an allocation,
      persists `generated_documents`

## Milestone 9 — Audit trail

- [ ] `services/audit.py` — wraps mutating operations, writes `audit_log` with before/after
      JSONB; other services call into this rather than callers hitting `audit_log` directly

---

## Open design forks (from SCHEMA.md §5)

- **Fund strategy**: seed data (`hurdle_rate`, `carry_rate`) points at a PE/VC-style closed-
  end fund — waterfall logic in Milestone 4 should target that cleanly rather than
  generalizing across strategies.
- **Reserve policy**: resolved as a fixed $15,000 default (`services/reserve.py`), not a
  per-account model — the schema has no concept of separate bank accounts to sum.
- **Determination inputs**: resolved as ledger-only, not `investments`-derived. Practitioner
  guidance: fund admins look at the general ledger for future-dated (held) calls and
  distributions already recorded there — anything not on the ledger isn't considered.
  `services/portfolio.py` was built and then removed for this reason; `investments` may
  still be useful for reporting later, but it isn't a determination input. Also resolved:
  distribution sizing doesn't need to trace back to realized proceeds before proposing —
  `distributions.recallable` already exists to correct an over-distribution after the fact.
