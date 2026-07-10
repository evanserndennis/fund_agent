from datetime import date
from decimal import Decimal

from fund_agent.services.ledger import cash_balance
from fund_agent.services.reserve import get_reserve_amount


def available_cash(cur, fund_id: str, as_of: date) -> Decimal:
    return cash_balance(cur, fund_id=fund_id, as_of=as_of) - get_reserve_amount()


def distribution_amount(cur, fund_id: str, as_of: date) -> Decimal:
    return max(Decimal("0.00"), available_cash(cur, fund_id=fund_id, as_of=as_of))
