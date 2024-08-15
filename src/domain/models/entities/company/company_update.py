from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class CompanyUpdate(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    inactivity_time: str = Field(default=None)
    nit: str = Field(..., max_length=255)
    state: bool = Field(default=True)
