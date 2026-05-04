# SPEC-006 T5
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class PasswordResetTokenSave(BaseModel):
    user_id: UUID = Field(...)
    token: str = Field(...)
    expires_at: datetime = Field(...)
    state: bool = Field(default=True)
