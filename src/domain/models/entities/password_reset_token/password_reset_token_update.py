# SPEC-006 T5
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class PasswordResetTokenUpdate(BaseModel):
    id: UUID = Field(...)
    user_id: UUID = Field(...)
    token: str = Field(...)
    expires_at: datetime = Field(...)
    used_at: Optional[datetime] = Field(default=None)
    state: bool = Field(default=True)
