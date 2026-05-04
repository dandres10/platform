# SPEC-006 T13
from pydantic import BaseModel, Field


class ForgotPasswordResponse(BaseModel):
    message: str = Field(...)
