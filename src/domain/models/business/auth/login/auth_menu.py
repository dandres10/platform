from pydantic import UUID4, BaseModel, Field

from src.domain.models.business.auth.login.auth_login_response import PermissionLoginResponse

class AuthMenu(BaseModel):
    company: UUID4 = Field(...)
    permissions: list[PermissionLoginResponse] = Field(...)