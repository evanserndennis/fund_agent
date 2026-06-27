from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Literal


class CapitalCall(BaseModel):
    id: str
    fund_id: str
    agent_run_id: str
    call_number: int
    call_date: date
    due_date: date
    total_amount: Decimal
    purpose: Literal["investment", "expense", "fee"]
    status: Literal["draft", "proposed", "approved", "issued", "funded"]
