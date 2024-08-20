

from pydantic import UUID4, BaseModel, Field


class Security(BaseModel):
    email: str = Field(...)
    location: UUID4 = Field(...)