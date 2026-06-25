from seed_helper import uid


# (account_code, account_name, account_type, normal_balance)
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


def seed_chart_of_accounts(cur) -> list[dict]:
    accounts = []
    for code, name, account_type, normal_balance in COA_DEF:
        accounts.append(_account_builder(code, name, account_type, normal_balance))
    _insert_accounts(cur, accounts)
    return accounts


def _account_builder(code: str, name: str, account_type: str, normal_balance: str) -> dict:
    return {
        "id": uid(),
        "account_code": code,
        "account_name": name,
        "account_type": account_type,
        "normal_balance": normal_balance,
    }


def _insert_accounts(cur, accounts: list[dict]) -> None:
    cur.executemany(
        """
        INSERT INTO chart_of_accounts
            (id, account_code, account_name, account_type, normal_balance)
        VALUES (%s, %s, %s, %s, %s)
        """,
        [
            (a["id"], a["account_code"], a["account_name"], a["account_type"], a["normal_balance"])
            for a in accounts
        ],
    )
