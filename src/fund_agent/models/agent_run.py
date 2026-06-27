from pydantic import BaseModel
from typing import Literal
from datetime import datetime
from decimal import Decimal


class AgentRun(BaseModel):
    id: str
    trigger: Literal["scheduled", "manual"]
    started_at: datetime
    inputs_snapshot: dict
    rationale: dict
    confidence: Decimal
    model_version: str
