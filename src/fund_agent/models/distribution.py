from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Literal, Optional


class Distribution(BaseModel):
    id: str
    fund_id: str
    agent_run_id: Optional[str] = None
    distribution_number: int
    distribution_date: date
    total_amount: Decimal
    type: Literal["return_of_capital", "income", "gain"]
    recallable: bool
    status: Literal["draft", "proposed", "approved", "issued"]
