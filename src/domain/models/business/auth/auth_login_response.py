from typing import Optional
from pydantic import UUID4, BaseModel


from pydantic import BaseModel, Field


class AuthLoginResponse(BaseModel):
    user_id: Optional[UUID4] = Field(default=None)
    rol_id: Optional[UUID4] = Field(default=None)
    rol_name: str = Field(default=None)
    rol_code: str = Field(default=None)
    platform_id: Optional[UUID4] = Field(default=None)
    language_id: Optional[UUID4] = Field(default=None)
    location_id: Optional[UUID4] = Field(default=None)
    currency_id: Optional[UUID4] = Field(default=None)
    """ token_expiration_minutes: int = Field(default=None) """
    email: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    phone: Optional[str] = Field(default=None)
    state: Optional[bool] = Field(default=None)

