
from pydantic import BaseModel, Field


class WSRequest(BaseModel):
    language: str = Field(...)
    timezone: str = Field(...)
    token: str = Field(...)
