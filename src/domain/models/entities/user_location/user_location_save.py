from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class UserLocationSave(BaseModel):
    user_id: Optional[UUID4] = Field(default=None)
    location_id: Optional[UUID4] = Field(default=None)
    state: bool = Field(default=True)
