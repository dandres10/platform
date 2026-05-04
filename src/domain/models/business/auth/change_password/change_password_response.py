# SPEC-006 T12
from pydantic import BaseModel, Field


class ChangePasswordResponse(BaseModel):
    message: str = Field(...)
