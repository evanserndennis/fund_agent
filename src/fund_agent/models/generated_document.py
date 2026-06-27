from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional


class GeneratedDocument(BaseModel):
    id: str
    template_id: Optional[str] = None
    doc_type: Optional[str] = None
    allocation_id: Optional[str] = None
    investor_id: str
    file_path: Optional[str] = None
    generated_at: datetime
    status: Literal["draft", "sent"]
