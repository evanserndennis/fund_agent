from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AuditLog(BaseModel):
    id: str
    actor: str
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    before: Optional[dict] = None
    after: Optional[dict] = None
    at: datetime
    