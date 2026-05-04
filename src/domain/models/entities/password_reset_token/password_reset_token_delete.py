# SPEC-006 T5
from uuid import UUID

from pydantic import BaseModel, Field


class PasswordResetTokenDelete(BaseModel):
    id: UUID = Field(...)
