from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class UserCountryUpdate(BaseModel):
    id: UUID4 = Field(...)
    user_id: UUID4 = Field(...)
    country_id: UUID4 = Field(...)
    state: bool = Field(default=True)
