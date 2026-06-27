from pydantic import BaseModel
from typing import Literal


class DocumentTemplate(BaseModel):
    id: str
    doc_type: Literal["call_notice", "distribution_notice"]
    version: int
    body: str
