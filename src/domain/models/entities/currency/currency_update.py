from pydantic import BaseModel, UUID4, Field, field_validator
from typing import Optional
from datetime import datetime


class CurrencyUpdate(BaseModel):
    id: Optional[UUID4] = Field(default=None)
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=10)
    symbol: str = Field(..., max_length=10)
    state: bool = Field(default=True)

