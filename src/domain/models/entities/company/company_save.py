from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class CompanySave(BaseModel):
    name: str = Field(..., max_length=255)
    inactivity_time: int = Field(default=20)
    nit: str = Field(..., max_length=255)
    state: bool = Field(default=True)
    # SPEC-001 T6.5
    base_currency_id: UUID4 = Field(...)
