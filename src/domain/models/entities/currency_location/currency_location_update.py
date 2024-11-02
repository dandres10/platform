from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class CurrencyLocationUpdate(BaseModel):
    id: UUID4 = Field(...)
    currency_id: UUID4 = Field(...)
    location_id: UUID4 = Field(...)
    state: bool = Field(default=True)
