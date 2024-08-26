from pydantic import BaseModel, Field


class AuthLogoutResponse(BaseModel):
    message: str = Field(...)