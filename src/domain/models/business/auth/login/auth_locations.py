from pydantic import UUID4, BaseModel, Field


class AuthLocations(BaseModel):
    user_id: UUID4 = Field(...)
    company_id: UUID4 = Field(...)
