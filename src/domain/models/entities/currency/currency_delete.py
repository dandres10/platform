from pydantic import BaseModel, UUID4, Field, field_validator
from typing import Optional
from datetime import datetime


class CurrencyDelete(BaseModel):
    id: Optional[UUID4] = Field(default=None)
