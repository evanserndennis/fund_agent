from datetime import date
from decimal import Decimal

from fund_agent.services.trial_balance import trial_balance

CASH_ACCOUNT_CODE = "1001"


def cash_balance(cur, fund_id: str, as_of: date) -> Decimal:
    cur.execute(
        "SELECT id FROM chart_of_accounts WHERE account_code = %(account_code)s",
        {"account_code": CASH_ACCOUNT_CODE},
    )
    cash_account_id = cur.fetchone()[0]

    return trial_balance(
        cur=cur,
        fund_id=fund_id,
        as_of=as_of
    )[cash_account_id]
