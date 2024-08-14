from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class PlatformSave(BaseModel):
    language_id: Optional[UUID4] = Field(default=None)
    location_id: Optional[UUID4] = Field(default=None)
    currency_location_id: Optional[UUID4] = Field(default=None)
    token_expiration_minutes: int = Field(default=60)
    refresh_token_expiration_minutes: int = Field(default=62)
