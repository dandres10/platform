from pydantic import BaseModel, Field


class AuthRefreshTokenResponse(BaseModel):
    token: str = Field(...)
