from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class PlatformUpdate(BaseModel):
    id: UUID4 = Field(...)
    language_id: UUID4 = Field(...)
    location_id: UUID4 = Field(...)
    currency_id: UUID4 = Field(...)
    token_expiration_minutes: int = Field(default=60)
    refresh_token_expiration_minutes: int = Field(default=62)
