from pydantic import BaseModel
from decimal import Decimal


class CallAllocation(BaseModel):
    id: str
    call_id: str
    investor_id: str
    amount: Decimal
    basis_pct: Decimal
    unfunded_before: Decimal
    unfunded_after: Decimal
    status: str