from pydantic import BaseModel
from decimal import Decimal
from typing import Literal


class Investment(BaseModel):
    id: str
    fund_id: str
    company_name: str
    invested_amount: Decimal
    current_value: Decimal
    realized_proceeds: Decimal
    status: Literal['active', 'partially_realized', 'realized', 'written_off']
    