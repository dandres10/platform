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


class CurrencyLoginResponse(BaseModel):
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

class PermissionToken(BaseModel):
    id: str = Field(...)
    name: str = Field(..., max_length=255)


class MenuLoginResponse(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=100)
    label: str = Field(..., max_length=300)
    description: str = Field(..., max_length=300)
    top_id: UUID4 = Field(...)
    route: str = Field(..., max_length=300)
    state: bool = Field(default=True)
    icon: str = Field(..., max_length=50)


class PlatformConfiguration(BaseModel):
    user: UserLoginResponse = Field(...)
    currency: CurrencyLoginResponse = Field(...)
    location: LocationLoginResponse = Field(...)
    language: LanguageLoginResponse = Field(...)
    platform: PlatformLoginResponse = Field(...)
    country: CountryLoginResponse = Field(...)
    company: CompanyLoginResponse = Field(...)
    rol: RolLoginResponse = Field(...)
    permissions: List[PermissionLoginResponse] = Field(...)
    menu: List[MenuLoginResponse] = Field(...)


class PlatformVariations(BaseModel):
    currencies: List[CurrencyLoginResponse] = Field(...)
    locations: List[LocationLoginResponse] = Field(...)
    languages: List[LanguageLoginResponse] = Field(...)


class AuthLoginResponse(BaseModel):
    platform_configuration: PlatformConfiguration = Field(...)
    platform_variations: PlatformVariations = Field(...)
    token: str = Field(...)
