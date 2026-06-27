from pydantic import BaseModel
from decimal import Decimal


class DistributionAllocation(BaseModel):
    id: str
    distribution_id: str
    investor_id: str
    return_of_capital: Decimal
    pref_return: Decimal
    profit: Decimal
    gp_carry: Decimal
    total: Decimal
