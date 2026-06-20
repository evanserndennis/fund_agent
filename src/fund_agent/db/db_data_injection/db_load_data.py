import calendar
import json
import random
import uuid
from decimal import Decimal
from datetime import date, timedelta

from db_connection import get_db_connection

random.seed(42)


def uid():
    return str(uuid.uuid4())


def d(val):
    return Decimal(str(round(float(val), 2)))


# ── 1. Fund ───────────────────────────────────────────────────────────────────

fund_id = uid()

FUND = (
    fund_id, "Apex Ventures III, L.P.", "USD", 2021, 10,
    d(0.0200), d(0.0800), d(0.2000), "investing",
)

# ── 2. Investors ──────────────────────────────────────────────────────────────

gp_id = uid()
GP = (
    gp_id, "Apex GP LLC", "GP", "XX-9999999", "approved",
    json.dumps({"bank": "JPMorgan", "account": "****4210"}),
    json.dumps({"email": "gp@apexventures.com"}),
)

LP_NAMES = [
    ("Blackrock Alternatives Fund",     "institution"),
    ("State Street Pension Trust",       "institution"),
    ("Harvard Endowment Management",     "institution"),
    ("CalPERS Private Markets",          "institution"),
    ("Ontario Teachers Private Equity",  "institution"),
    ("Sovereign Capital Partners",       "institution"),
    ("Wellington Diversified Fund",      "institution"),
    ("Meridian Family Office LLC",       "individual"),
    ("Pemberton Capital Group",          "institution"),
    ("Horizon Wealth Management",        "institution"),
    ("Cascade Asset Management",         "institution"),
    ("Sterling Point Advisors",          "individual"),
]

lp_ids = []
lp_rows = []
for name, inv_type in LP_NAMES:
    lid = uid()
    lp_ids.append(lid)
    lp_rows.append((
        lid, name, inv_type,
        f"XX-{random.randint(1000000, 9999999)}", "approved",
        json.dumps({"bank": random.choice(["JPMorgan", "Citi", "BofA", "Wells Fargo"]),
                    "account": f"****{random.randint(1000, 9999)}"}),
        json.dumps({"email": f"ir@{name.lower().replace(' ', '')[:14]}.com"}),
    ))

# ── 3. Closings ───────────────────────────────────────────────────────────────

closing_ids = [uid(), uid(), uid()]
CLOSINGS = [
    (closing_ids[0], fund_id, 1, date(2021, 6, 30)),
    (closing_ids[1], fund_id, 2, date(2021, 10, 15)),
    (closing_ids[2], fund_id, 3, date(2022, 2, 28)),
]

# ── 4. Commitments ────────────────────────────────────────────────────────────

LP_COMMITMENT_AMOUNTS = [
    25_000_000, 30_000_000, 20_000_000, 35_000_000,
    15_000_000, 10_000_000, 12_000_000,  5_000_000,
    18_000_000,  8_000_000, 14_000_000,  6_000_000,
]
CLOSE_ASSIGNMENT = [0] * 7 + [1] * 3 + [2] * 2

COMMITMENTS = [(uid(), fund_id, gp_id, closing_ids[0], d(3_800_000), date(2021, 6, 30))]
lp_commitment_ids = []
for i, (lid, amount) in enumerate(zip(lp_ids, LP_COMMITMENT_AMOUNTS)):
    cid = uid()
    lp_commitment_ids.append(cid)
    close_idx = CLOSE_ASSIGNMENT[i]
    COMMITMENTS.append((cid, fund_id, lid, closing_ids[close_idx], d(amount), CLOSINGS[close_idx][3]))

# ── 5. Chart of accounts ──────────────────────────────────────────────────────

acct = {}  # account_code -> UUID
COA_DEF = [
    ("1001", "Cash and Cash Equivalents",   "asset",     "debit"),
    ("1100", "LP Capital Receivable",        "asset",     "debit"),
    ("1200", "Investments at Cost",          "asset",     "debit"),
    ("1210", "Unrealized Gain / (Loss)",     "asset",     "debit"),
    ("1300", "Accrued Interest Receivable",  "asset",     "debit"),
    ("2001", "Accounts Payable",             "liability", "credit"),
    ("2100", "Distributions Payable",        "liability", "credit"),
    ("3001", "GP Capital Account",           "equity",    "credit"),
    ("3100", "LP Capital Contributions",     "equity",    "credit"),
    ("3200", "LP Distributed Earnings",      "equity",    "credit"),
    ("3300", "Unrealized Appreciation",      "equity",    "credit"),
    ("4001", "Management Fee Income",        "income",    "credit"),
    ("4100", "Interest and Dividend Income", "income",    "credit"),
    ("4200", "Realized Gain on Investments", "income",    "credit"),
    ("5001", "Fund Operating Expenses",      "expense",   "debit"),
]
COA_ROWS = []
for code, name, atype, nbal in COA_DEF:
    aid = uid()
    acct[code] = aid
    COA_ROWS.append((aid, code, name, atype, nbal))

# ── 6. Investments ────────────────────────────────────────────────────────────

PORTFOLIO = [
    ("TechCorp Inc.",          35_000_000, 52_000_000,  0,          "active"),
    ("MedDevice Solutions",    28_000_000, 41_500_000,  0,          "active"),
    ("GreenEnergy Systems",    22_000_000, 18_000_000,  0,          "active"),
    ("FinTech Platforms LLC",  18_000_000, 32_000_000,  0,          "active"),
    ("DataStream Analytics",   15_000_000, 28_000_000,  0,          "active"),
    ("CloudBase Inc.",         12_000_000, 12_000_000,  18_000_000, "partially_realized"),
    ("RetailAI Corp",          10_000_000, 14_500_000,  0,          "active"),
    ("BioLab Sciences",         8_000_000,  0,           0,          "written_off"),
    ("Supply Chain Co.",       20_000_000,  0,          35_000_000, "realized"),
    ("PropTech Ventures",      14_000_000, 19_000_000,  0,          "active"),
]
investment_ids = []
INVESTMENTS = []
for company, invested, current, realized, status in PORTFOLIO:
    inv_id = uid()
    investment_ids.append(inv_id)
    INVESTMENTS.append((
        inv_id, fund_id, company, d(invested),
        d(current) if current else None,
        d(realized), status,
    ))

# ── 7. Agent runs ─────────────────────────────────────────────────────────────

RUN_DATES = [
    date(2021, 9, 1),  date(2021, 11, 1), date(2022, 2, 1),  date(2022, 5, 1),
    date(2022, 8, 1),  date(2022, 11, 1), date(2023, 2, 1),  date(2023, 5, 1),
    date(2023, 8, 1),  date(2023, 11, 1), date(2024, 2, 1),  date(2024, 5, 1),
    date(2024, 8, 1),  date(2024, 11, 1), date(2025, 2, 1),
]
agent_run_ids = []
AGENT_RUNS = []
for run_date in RUN_DATES:
    run_id = uid()
    agent_run_ids.append(run_id)
    cash = random.randint(5_000_000, 25_000_000)
    pipeline = random.randint(0, 40_000_000)
    AGENT_RUNS.append((
        run_id,
        random.choice(["scheduled", "manual"]),
        f"{run_date}T09:00:00+00:00",
        json.dumps({"cash_balance": cash, "pipeline_obligations": pipeline,
                    "reserve_requirement": 2_000_000, "total_committed": 201_800_000}),
        json.dumps({"analysis": f"Cash ${cash:,} vs pipeline ${pipeline:,}",
                    "recommendation": "capital_call" if pipeline > cash else "no_action"}),
        d(random.uniform(0.80, 0.97)),
        "claude-opus-4",
    ))

# ── 8. Capital calls ──────────────────────────────────────────────────────────

CALL_DEF = [
    (date(2021, 9, 15),  date(2021, 9, 30),  20_000_000, "investment", 0),
    (date(2021, 11, 15), date(2021, 11, 30), 30_000_000, "investment", 1),
    (date(2022, 2, 15),  date(2022, 3, 1),   25_000_000, "investment", 2),
    (date(2022, 5, 15),  date(2022, 5, 31),  18_000_000, "investment", 3),
    (date(2022, 8, 15),  date(2022, 8, 31),  15_000_000, "investment", 4),
    (date(2022, 11, 15), date(2022, 11, 30), 12_000_000, "investment", 5),
    (date(2023, 2, 15),  date(2023, 3, 1),   10_000_000, "expense",    6),
    (date(2023, 5, 15),  date(2023, 5, 31),  20_000_000, "investment", 7),
    (date(2023, 8, 15),  date(2023, 8, 31),  14_000_000, "investment", 8),
    (date(2023, 11, 15), date(2023, 11, 30),  8_000_000, "fee",        9),
]
call_ids = []
CAPITAL_CALLS = []
for i, (call_date, due_date, total, purpose, run_idx) in enumerate(CALL_DEF):
    call_id = uid()
    call_ids.append(call_id)
    CAPITAL_CALLS.append((
        call_id, fund_id, agent_run_ids[run_idx], i + 1,
        call_date, due_date, d(total), purpose, "funded",
    ))

# ── 9. Call allocations ───────────────────────────────────────────────────────

TOTAL_LP_COMMIT = sum(LP_COMMITMENT_AMOUNTS)
LP_BASIS_PCTS = [d(amt / TOTAL_LP_COMMIT) for amt in LP_COMMITMENT_AMOUNTS]

unfunded_tracker = {lid: d(amt) for lid, amt in zip(lp_ids, LP_COMMITMENT_AMOUNTS)}
CALL_ALLOCATIONS = []
for call_id, (_, _, total, _, _) in zip(call_ids, CALL_DEF):
    for lid, basis_pct in zip(lp_ids, LP_BASIS_PCTS):
        amount = d(total * float(basis_pct))
        before = unfunded_tracker[lid]
        after = d(float(before) - float(amount))
        unfunded_tracker[lid] = after
        CALL_ALLOCATIONS.append((uid(), call_id, lid, amount, basis_pct, before, after, "funded"))

# ── 10. Distributions ─────────────────────────────────────────────────────────

DIST_DEF = [
    (date(2023, 6, 30),  35_000_000, "return_of_capital", False, 7),
    (date(2023, 12, 15), 18_000_000, "gain",              False, 9),
    (date(2024, 3, 31),  12_000_000, "income",            False, 11),
    (date(2024, 9, 30),  25_000_000, "return_of_capital", True,  13),
    (date(2025, 1, 15),  10_000_000, "gain",              False, 14),
]
dist_ids = []
DISTRIBUTIONS = []
for i, (dist_date, total, dist_type, recallable, run_idx) in enumerate(DIST_DEF):
    dist_id = uid()
    dist_ids.append(dist_id)
    DISTRIBUTIONS.append((
        dist_id, fund_id, agent_run_ids[run_idx], i + 1,
        dist_date, d(total), dist_type, recallable, "issued",
    ))

# ── 11. Distribution allocations ──────────────────────────────────────────────

DIST_ALLOCATIONS = []
for dist_id, (_, total, dist_type, _, _) in zip(dist_ids, DIST_DEF):
    for lid, basis_pct in zip(lp_ids, LP_BASIS_PCTS):
        lp_total = d(total * float(basis_pct))
        if dist_type == "return_of_capital":
            roc, pref, profit, carry = lp_total, d(0), d(0), d(0)
        elif dist_type == "income":
            roc    = d(0)
            pref   = d(float(lp_total) * 0.60)
            profit = d(float(lp_total) * 0.30)
            carry  = d(float(lp_total) * 0.10)
        else:  # gain
            roc    = d(0)
            pref   = d(float(lp_total) * 0.30)
            profit = d(float(lp_total) * 0.50)
            carry  = d(float(lp_total) * 0.20)
        DIST_ALLOCATIONS.append((uid(), dist_id, lid, roc, pref, profit, carry, lp_total))

# ── 12. Document templates ────────────────────────────────────────────────────

tmpl_call_id = uid()
tmpl_dist_id = uid()
DOC_TEMPLATES = [
    (
        tmpl_call_id, "call_notice", 1,
        "Dear {{investor_name}},\n\nYou are hereby notified that Apex Ventures III, L.P. "
        "has issued Capital Call #{{call_number}} in the amount of USD {{amount}}. "
        "Payment is due by {{due_date}}.\n\nRegards,\nApex GP LLC",
    ),
    (
        tmpl_dist_id, "distribution_notice", 1,
        "Dear {{investor_name}},\n\nApex Ventures III, L.P. is pleased to inform you of "
        "a distribution in the amount of USD {{amount}} on {{distribution_date}}. "
        "Funds will be wired to your account on file.\n\nRegards,\nApex GP LLC",
    ),
]

# ── 13. Generated documents ───────────────────────────────────────────────────

GENERATED_DOCS = []
for i, call_id in enumerate(call_ids[:3]):
    for lid in lp_ids:
        GENERATED_DOCS.append((
            uid(), tmpl_call_id, "call_notice", None, lid,
            f"/docs/calls/call_{i+1}_{lid[:8]}.pdf",
            f"{CALL_DEF[i][0]}T10:30:00+00:00", "sent",
        ))
for i, dist_id in enumerate(dist_ids):
    for lid in lp_ids:
        GENERATED_DOCS.append((
            uid(), tmpl_dist_id, "distribution_notice", None, lid,
            f"/docs/distributions/dist_{i+1}_{lid[:8]}.pdf",
            f"{DIST_DEF[i][0]}T10:30:00+00:00", "sent",
        ))

# ── 14. Agent decisions ───────────────────────────────────────────────────────

AGENT_DECISIONS = []
for i, run_id in enumerate(agent_run_ids):
    if i < len(call_ids):
        dec_type = "call"
        data = {"call_number": i + 1, "proposed_amount": CALL_DEF[i][2]}
        needs_approval = True
    elif i == len(call_ids):
        dec_type = "no_action"
        data = {"reason": "insufficient realized proceeds for distribution"}
        needs_approval = False
    elif i - len(call_ids) - 1 < len(dist_ids):
        dist_idx = i - len(call_ids) - 1
        dec_type = "distribution"
        data = {"distribution_number": dist_idx + 1, "proposed_amount": DIST_DEF[dist_idx][1]}
        needs_approval = True
    else:
        dec_type = "no_action"
        data = {"reason": "cash reserves adequate, no action required"}
        needs_approval = False
    AGENT_DECISIONS.append((uid(), run_id, dec_type, json.dumps(data), needs_approval))

# ── 15. Approvals ─────────────────────────────────────────────────────────────

APPROVALS = []
for call_id, (call_date, *_) in zip(call_ids, CALL_DEF):
    APPROVALS.append((
        uid(), "capital_call", call_id, "CFO", "approved",
        "Reviewed and approved per investment committee authorization.",
        f"{call_date}T08:00:00+00:00",
    ))
for dist_id, (dist_date, *_) in zip(dist_ids, DIST_DEF):
    APPROVALS.append((
        uid(), "distribution", dist_id, "CFO", "approved",
        "Distribution approved following waterfall calculation review.",
        f"{dist_date}T08:00:00+00:00",
    ))

# ── 16. Journal entries & lines (~490 journal lines) ─────────────────────────

journal_entries = []
journal_lines = []


def je(entry_date, description, source="system"):
    je_id = uid()
    journal_entries.append((je_id, fund_id, entry_date, description, source, True, None))
    return je_id


def jl(entry_id, code, investor_id, debit=0, credit=0, memo=""):
    journal_lines.append((uid(), entry_id, acct[code], investor_id, d(debit), d(credit), memo))


# A — Capital call issuance: 10 entries × 2 lines = 20 lines
for i, (call_date, _, total, purpose, _) in enumerate(CALL_DEF):
    eid = je(call_date, f"Capital Call #{i+1} issued — {purpose}")
    jl(eid, "1100", None, debit=total,  memo=f"LP Capital Receivable — Call #{i+1}")
    jl(eid, "3100", None, credit=total, memo=f"LP Capital Contributions — Call #{i+1}")

# B — Capital receipt per LP: 10 calls × 12 LPs = 120 entries × 2 lines = 240 lines
for i, (_, due_date, total, _, _) in enumerate(CALL_DEF):
    for lid, basis_pct in zip(lp_ids, LP_BASIS_PCTS):
        alloc = float(d(total * float(basis_pct)))
        receipt_date = due_date + timedelta(days=random.randint(0, 5))
        eid = je(receipt_date, f"Capital Call #{i+1} receipt — LP {lid[:8]}")
        jl(eid, "1001", lid, debit=alloc,  memo=f"Cash received — LP {lid[:8]}")
        jl(eid, "1100", lid, credit=alloc, memo=f"Receivable cleared — LP {lid[:8]}")

# C — Investment deployments: 10 entries × 2 lines = 20 lines
INVEST_DATES = [
    date(2021, 10, 1), date(2021, 12, 1), date(2022, 3, 1),  date(2022, 6, 1),
    date(2022, 9, 1),  date(2022, 12, 1), date(2023, 3, 1),  date(2023, 6, 1),
    date(2023, 9, 1),  date(2023, 12, 1),
]
for (company, invested, _, _, _), inv_date in zip(PORTFOLIO, INVEST_DATES):
    eid = je(inv_date, f"Investment in {company}")
    jl(eid, "1200", None, debit=invested,  memo=f"Investment at cost — {company}")
    jl(eid, "1001", None, credit=invested, memo=f"Cash deployed — {company}")

# D — Management fees, 16 quarters: 16 entries × 2 lines = 32 lines
def next_quarter_end(dt):
    m = dt.month + 3
    y = dt.year + (m - 1) // 12
    m = ((m - 1) % 12) + 1
    return date(y, m, calendar.monthrange(y, m)[1])


MGMT_FEE_QUARTERS = []
q = date(2021, 9, 30)
for _ in range(16):
    MGMT_FEE_QUARTERS.append(q)
    q = next_quarter_end(q)

QUARTERLY_FEE = d(201_800_000 * 0.02 / 4)
for q in MGMT_FEE_QUARTERS:
    eid = je(q, f"Management fee — quarter ended {q}")
    jl(eid, "5001", None, debit=float(QUARTERLY_FEE),  memo="Mgmt fee expense")
    jl(eid, "4001", None, credit=float(QUARTERLY_FEE), memo="Mgmt fee income")

# E — Distribution issuance: 5 entries × 2 lines = 10 lines
for i, (dist_date, total, dist_type, _, _) in enumerate(DIST_DEF):
    eid = je(dist_date, f"Distribution #{i+1} — {dist_type}")
    jl(eid, "3100", None, debit=total,  memo=f"LP Capital — Distribution #{i+1}")
    jl(eid, "2100", None, credit=total, memo=f"Distributions payable — #{i+1}")

# F — Distribution payments per LP: 5 × 12 = 60 entries × 2 lines = 120 lines
for i, (dist_date, total, _, _, _) in enumerate(DIST_DEF):
    for lid, basis_pct in zip(lp_ids, LP_BASIS_PCTS):
        lp_amt = float(d(total * float(basis_pct)))
        pay_date = dist_date + timedelta(days=random.randint(3, 10))
        eid = je(pay_date, f"Distribution #{i+1} payment — LP {lid[:8]}")
        jl(eid, "2100", lid, debit=lp_amt,  memo=f"Distributions payable cleared — LP {lid[:8]}")
        jl(eid, "1001", lid, credit=lp_amt, memo=f"Cash paid — LP {lid[:8]}")

# G — Realized gain entries: 4 entries × 2 lines = 8 lines
eid = je(date(2023, 7, 1), "Proceeds received — CloudBase Inc. partial exit")
jl(eid, "1001", None, debit=18_000_000,  memo="Cash proceeds — CloudBase partial")
jl(eid, "4200", None, credit=18_000_000, memo="Realized gain — CloudBase Inc.")

eid = je(date(2023, 7, 1), "Cost basis reduction — CloudBase Inc.")
jl(eid, "4200", None, debit=6_000_000,  memo="Cost basis offset — partial realization")
jl(eid, "1200", None, credit=6_000_000, memo="Investment at cost reduced — CloudBase")

eid = je(date(2024, 1, 15), "Proceeds received — Supply Chain Co. full exit")
jl(eid, "1001", None, debit=35_000_000,  memo="Cash proceeds — Supply Chain exit")
jl(eid, "4200", None, credit=35_000_000, memo="Realized gain — Supply Chain Co.")

eid = je(date(2024, 1, 15), "Cost basis removal — Supply Chain Co.")
jl(eid, "4200", None, debit=20_000_000,  memo="Cost basis offset — full exit")
jl(eid, "1200", None, credit=20_000_000, memo="Investment at cost removed — Supply Chain")

# H — BioLab write-off: 1 entry × 2 lines = 2 lines
eid = je(date(2024, 6, 30), "Investment write-off — BioLab Sciences")
jl(eid, "5001", None, debit=8_000_000,  memo="Write-off expense — BioLab Sciences")
jl(eid, "1200", None, credit=8_000_000, memo="Investment at cost removed — BioLab")

# I — Interest income, first 8 quarters: 8 entries × 2 lines = 16 lines
for q in MGMT_FEE_QUARTERS[:8]:
    income = random.randint(50_000, 180_000)
    eid = je(q, f"Interest income — quarter ended {q}")
    jl(eid, "1001", None, debit=income,  memo="Interest income received")
    jl(eid, "4100", None, credit=income, memo="Interest and dividend income")

# J — Operating expenses: 10 entries × 2 lines = 20 lines
EXPENSE_ENTRIES = [
    (date(2021, 12, 31), "Legal fees — fund formation",   90_000),
    (date(2022, 3, 31),  "Audit fees — annual",           75_000),
    (date(2022, 6, 30),  "D&O insurance premium",         42_000),
    (date(2022, 9, 30),  "Administrative expenses",       18_500),
    (date(2022, 12, 31), "Tax preparation fees",          55_000),
    (date(2023, 3, 31),  "Advisory fees",                 30_000),
    (date(2023, 6, 30),  "Compliance consulting",         22_000),
    (date(2023, 9, 30),  "Fund administration fees",      48_000),
    (date(2023, 12, 31), "Annual audit fees",             80_000),
    (date(2024, 3, 31),  "Legal expenses — portfolio",    35_000),
]
for exp_date, desc, amount in EXPENSE_ENTRIES:
    eid = je(exp_date, desc)
    jl(eid, "5001", None, debit=amount,  memo=desc)
    jl(eid, "2001", None, credit=amount, memo=f"Payable — {desc}")

# ── 17. Audit log ─────────────────────────────────────────────────────────────

AUDIT_LOG = []
for call_id, (call_date, _, total, purpose, _) in zip(call_ids, CALL_DEF):
    AUDIT_LOG.append((
        uid(), "agent", "create", "capital_call", call_id,
        json.dumps(None),
        json.dumps({"status": "draft", "total_amount": float(d(total)), "purpose": purpose}),
        f"{call_date}T09:05:00+00:00",
    ))
    AUDIT_LOG.append((
        uid(), "CFO", "approve", "capital_call", call_id,
        json.dumps({"status": "proposed"}),
        json.dumps({"status": "approved"}),
        f"{call_date}T11:00:00+00:00",
    ))
for dist_id, (dist_date, total, dist_type, _, _) in zip(dist_ids, DIST_DEF):
    AUDIT_LOG.append((
        uid(), "agent", "create", "distribution", dist_id,
        json.dumps(None),
        json.dumps({"status": "draft", "total_amount": float(d(total)), "type": dist_type}),
        f"{dist_date}T09:05:00+00:00",
    ))
    AUDIT_LOG.append((
        uid(), "CFO", "approve", "distribution", dist_id,
        json.dumps({"status": "proposed"}),
        json.dumps({"status": "approved"}),
        f"{dist_date}T11:00:00+00:00",
    ))

# ── Insert everything ─────────────────────────────────────────────────────────

with get_db_connection() as conn:
    with conn.cursor() as cur:

        cur.execute("""
            INSERT INTO funds
                (id, name, base_currency, vintage_year, fund_term,
                 mgmt_fee_rate, hurdle_rate, carry_rate, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, FUND)

        cur.execute("""
            INSERT INTO investors
                (id, legal_name, type, tax_id, kyc_status, banking_ref, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, GP)
        cur.executemany("""
            INSERT INTO investors
                (id, legal_name, type, tax_id, kyc_status, banking_ref, contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, lp_rows)

        cur.executemany("""
            INSERT INTO closings (id, fund_id, closing_number, closing_date)
            VALUES (%s, %s, %s, %s)
        """, CLOSINGS)

        cur.executemany("""
            INSERT INTO commitments
                (id, fund_id, investor_id, closing_id, commitment_amount, commitment_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, COMMITMENTS)

        cur.executemany("""
            INSERT INTO chart_of_accounts
                (id, account_code, account_name, account_type, normal_balance)
            VALUES (%s, %s, %s, %s, %s)
        """, COA_ROWS)

        cur.executemany("""
            INSERT INTO investments
                (id, fund_id, company_name, invested_amount,
                 current_value, realized_proceeds, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, INVESTMENTS)

        cur.executemany("""
            INSERT INTO agent_runs
                (id, trigger, started_at, inputs_snapshot,
                 rationale, confidence, model_version)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, AGENT_RUNS)

        cur.executemany("""
            INSERT INTO capital_calls
                (id, fund_id, agent_run_id, call_number,
                 call_date, due_date, total_amount, purpose, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, CAPITAL_CALLS)

        cur.executemany("""
            INSERT INTO call_allocations
                (id, call_id, investor_id, amount,
                 basis_pct, unfunded_before, unfunded_after, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, CALL_ALLOCATIONS)

        cur.executemany("""
            INSERT INTO distributions
                (id, fund_id, agent_run_id, distribution_number,
                 distribution_date, total_amount, type, recallable, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, DISTRIBUTIONS)

        cur.executemany("""
            INSERT INTO distribution_allocations
                (id, distribution_id, investor_id,
                 return_of_capital, pref_return, profit, gp_carry, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, DIST_ALLOCATIONS)

        cur.executemany("""
            INSERT INTO document_templates (id, doc_type, version, body)
            VALUES (%s, %s, %s, %s)
        """, DOC_TEMPLATES)

        cur.executemany("""
            INSERT INTO generated_documents
                (id, template_id, doc_type, allocation_id,
                 investor_id, file_path, generated_at, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, GENERATED_DOCS)

        cur.executemany("""
            INSERT INTO agent_decisions
                (id, run_id, decision_type, supporting_data, requires_approval)
            VALUES (%s, %s, %s, %s, %s)
        """, AGENT_DECISIONS)

        cur.executemany("""
            INSERT INTO approvals
                (id, entity_type, entity_id, approver,
                 decision, comments, decided_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, APPROVALS)

        cur.executemany("""
            INSERT INTO journal_entries
                (id, fund_id, entry_date, description,
                 source, posted, reversal_of)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, journal_entries)

        cur.executemany("""
            INSERT INTO journal_lines
                (id, entry_id, account_id, investor_id,
                 debit, credit, memo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, journal_lines)

        cur.executemany("""
            INSERT INTO audit_log
                (id, actor, action, entity_type, entity_id,
                 before, after, at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, AUDIT_LOG)

    conn.commit()

print("Seed complete:")
print(f"  1 fund | 13 investors (1 GP + 12 LPs) | 3 closings | {len(COMMITMENTS)} commitments")
print(f"  {len(COA_ROWS)} chart of accounts | {len(INVESTMENTS)} investments")
print(f"  {len(AGENT_RUNS)} agent runs | {len(CAPITAL_CALLS)} capital calls | {len(CALL_ALLOCATIONS)} call allocations")
print(f"  {len(DISTRIBUTIONS)} distributions | {len(DIST_ALLOCATIONS)} distribution allocations")
print(f"  {len(DOC_TEMPLATES)} doc templates | {len(GENERATED_DOCS)} generated documents")
print(f"  {len(AGENT_DECISIONS)} agent decisions | {len(APPROVALS)} approvals")
print(f"  {len(journal_entries)} journal entries | {len(journal_lines)} journal lines")
print(f"  {len(AUDIT_LOG)} audit log entries")
