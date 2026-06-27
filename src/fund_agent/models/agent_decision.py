from pydantic import BaseModel
from typing import Literal, Optional


class AgentDecision(BaseModel):
    id: str
    run_id: str
    decision_type: Literal["call", "distribution", "no_action"]
    supporting_data: Optional[dict] = None
    requires_approval: bool
