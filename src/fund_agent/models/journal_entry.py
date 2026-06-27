from pydantic import BaseModel
from datetime import date
from typing import Literal, Optional


class JournalEntry(BaseModel):
    id: str
    fund_id: str
    entry_date: date
    description: Optional[str] = None
    source: Literal["manual", "system", "agent"]
    posted: bool
    reversal_of: Optional[str] = None
