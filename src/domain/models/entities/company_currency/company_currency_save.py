from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class CompanyCurrencySave(BaseModel):
    company_id: Optional[UUID4] = Field(default=None)
    currency_id: Optional[UUID4] = Field(default=None)
    is_base: bool = Field(default=False)
    state: bool = Field(default=True)
