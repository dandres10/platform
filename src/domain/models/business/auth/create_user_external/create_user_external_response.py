from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CreateUserExternalResponse(BaseModel):
    message: str = Field(...)
    # SPEC-006 T11.a
    user_id: Optional[UUID] = Field(default=None)
    token: Optional[str] = Field(default=None)
    refresh_token: Optional[str] = Field(default=None)

