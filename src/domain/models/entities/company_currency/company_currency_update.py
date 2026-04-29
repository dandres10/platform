from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class CompanyCurrencyUpdate(BaseModel):
    id: UUID4 = Field(...)
    currency_id: Optional[UUID4] = Field(default=None)
    is_base: Optional[bool] = Field(default=None)
    state: Optional[bool] = Field(default=None)
