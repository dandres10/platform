from typing import List, Optional
from pydantic import UUID4, BaseModel
from pydantic import BaseModel, Field


class UserLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    email: str = Field(..., max_length=255)
    first_name: str = Field(..., max_length=255)
    last_name: str = Field(..., max_length=255)
    phone: str = Field(..., max_length=20)
    state: bool = Field(...)


class CurrecyLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=10)
    symbol: str = Field(..., max_length=10)
    state: bool = Field(...)


class LocationLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    address: str = Field(...)
    city: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=100)
    main_location: bool = Field(...)
    state: bool = Field(...)


class LanguageLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)
    native_name: str = Field(..., max_length=100)
    state: bool = Field(...)


class PlatformLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    language_id: UUID4 = Field(...)
    location_id: UUID4 = Field(...)
    token_expiration_minutes: int = Field(...)
    currency_id: UUID4 = Field(...)


class CountryLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=10)
    phone_code: str = Field(..., max_length=10)
    state: bool = Field(...)


class CompanyLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    inactivity_time: int = Field(...)
    nit: str = Field(..., max_length=255)
    state: bool = Field(...)


class RolLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=255)
    description: str = Field(...)
    state: bool = Field(...)


class PermissionLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    description: str = Field(...)
    state: bool = Field(...)


class BasePlatformConfiguration(BaseModel):
    user: UserLoginResponse = Field(...)
    currecy: CurrecyLoginResponse = Field(...)
    location: LocationLoginResponse = Field(...)
    language: LanguageLoginResponse = Field(...)
    platform: PlatformLoginResponse = Field(...)
    country: CountryLoginResponse = Field(...)
    company: CompanyLoginResponse = Field(...)
    rol: RolLoginResponse = Field(...)
    permissions: List[PermissionLoginResponse] = Field(...)


class AuthLoginResponse(BaseModel):
    base_platform_configuration: BasePlatformConfiguration = Field(...)
