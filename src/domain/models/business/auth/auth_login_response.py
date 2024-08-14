from typing import Optional
from pydantic import UUID4, BaseModel


from pydantic import BaseModel, Field


class AuthLoginResponse(BaseModel):
    user_id: UUID4 = Field(...)
    rol_id: UUID4 = Field(...)
    """ rol_name: str = Field(...)
    rol_code: str = Field(...) """
    platform_id: UUID4 = Field(...)
    """ language_id: UUID4 = Field(...)
    location_id: UUID4 = Field(...)
    currency_id: UUID4 = Field(...)
    token_expiration_minutes: int = Field(...) """
    email: str = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    phone: str = Field(...)
    state: bool = Field(...)

