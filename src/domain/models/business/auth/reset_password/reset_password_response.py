# SPEC-006 T14
from pydantic import BaseModel, Field


class ResetPasswordResponse(BaseModel):
    message: str = Field(...)
