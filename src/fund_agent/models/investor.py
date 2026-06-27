from pydantic import BaseModel
from typing import Literal


class Investor(BaseModel):
    id: str
    legal_name: str
    type: Literal['GP', 'institution', 'individual']
    tax_id: str
    kyc_status: str
    banking_ref: dict
    contact: dict
