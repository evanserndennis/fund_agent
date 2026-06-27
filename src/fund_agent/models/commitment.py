from pydantic import BaseModel
from decimal import Decimal
from datetime import date


class Commitment(BaseModel):
    id: str
    fund_id: str
    investor_id: str
    closing_id: str
    commitment_amount: Decimal
    commitment_date: date
    