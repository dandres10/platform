from pydantic import UUID4, BaseModel, Field
from typing import Optional

from src.domain.models.business.auth.login.auth_login_response import PermissionLoginResponse

class AuthMenu(BaseModel):
    company: Optional[UUID4] = Field(default=None)
    permissions: list[PermissionLoginResponse] = Field(...)