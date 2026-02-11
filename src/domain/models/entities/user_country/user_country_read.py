from pydantic import UUID4, BaseModel, field_validator, Field

class UserCountryRead(BaseModel):
    id: UUID4 = Field(...)
