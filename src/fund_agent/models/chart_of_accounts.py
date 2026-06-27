from pydantic import BaseModel
from typing import Literal


class ChartOfAccounts(BaseModel):
    id: str
    account_code: str
    account_name: str
    account_type: Literal["asset", "liability", "equity", "income", "expense"]
    normal_balance: Literal["debit", "credit"]
