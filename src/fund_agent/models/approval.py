from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class Approval(BaseModel):
    id: str
    entity_type: Literal["capital_call", "distribution"]
    entity_id: str
    approver: str
    decision: Literal["approved", "rejected"]
    comments: str
    decided_at: datetime