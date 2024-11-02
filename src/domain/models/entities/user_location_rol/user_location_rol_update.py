from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class UserLocationRolUpdate(BaseModel):
    id: UUID4 = Field(...)
    user_id: UUID4 = Field(...)
    location_id: UUID4 = Field(...)
    rol_id: UUID4 = Field(...)
    state: bool = Field(default=True)
