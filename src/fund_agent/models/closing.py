from pydantic import BaseModel
from datetime import date


class Closing(BaseModel):
    id: str
    fund_id: str
    closing_number: int
    closing_date: date
    