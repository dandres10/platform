from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class CountrySave(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=10)
    phone_code: str = Field(..., max_length=10)
    state: bool = Field(default=True)
