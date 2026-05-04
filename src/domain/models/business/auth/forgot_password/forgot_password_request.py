# SPEC-006 T13
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, HttpUrl


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., description="Email del usuario que solicita reset")
    reset_link_base: Optional[HttpUrl] = Field(
        default=None,
        description="Base URL del frontend para el link de reset; el token se anexa como ?token=<uuid>. Ej: https://app.goluti.com/reset-password",
    )
