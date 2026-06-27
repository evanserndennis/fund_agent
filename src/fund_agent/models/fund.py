from pydantic import BaseModel
from decimal import Decimal
from typing import Literal


class Fund(BaseModel):
    id: str
    name: str
    base_currency: str
    vintage_year: int
    fund_term: int
    mgmt_fee_rate: Decimal
    hurdle_rate: Decimal
    carry_rate: Decimal
    status: Literal['fundraising', 'investing', 'harvesting', 'wound_down']
