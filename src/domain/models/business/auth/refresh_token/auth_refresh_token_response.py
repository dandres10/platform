from pydantic import BaseModel, Field
from src.domain.models.business.auth.login.auth_login_response import (
    PlatformConfiguration,
    PlatformVariations,
)


class AuthRefreshTokenResponse(BaseModel):
    platform_configuration: PlatformConfiguration = Field(...)
    platform_variations: PlatformVariations = Field(...)
    token: str = Field(...)
