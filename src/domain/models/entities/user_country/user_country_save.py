from pydantic import BaseModel, Field, UUID4
from typing import Optional

class UserCountrySave(BaseModel):
    user_id: Optional[UUID4] = Field(default=None)
    country_id: Optional[UUID4] = Field(default=None)
    state: bool = Field(default=True)
