# SPEC-006 T14
from pydantic import BaseModel, Field, field_validator

from src.core.classes.password import Password


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., min_length=8, max_length=64)
    new_password: str = Field(..., min_length=8, max_length=255)

    @field_validator("new_password")
    @classmethod
    def _validate_policy(cls, v: str) -> str:
        return Password.validate_policy(v)
