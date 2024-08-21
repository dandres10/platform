from pydantic import UUID4, BaseModel, EmailStr, Field


class AuthUserRoleAndPermissions(BaseModel):
    email: str = Field(...)
    location: UUID4 = Field(...)
