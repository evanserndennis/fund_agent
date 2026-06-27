from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class JournalLine(BaseModel):
    id: str
    entry_id: str
    account_id: str
    investor_id: Optional[str] = None
    debit: Decimal
    credit: Decimal
    memo: Optional[str] = None
