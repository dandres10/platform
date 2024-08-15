from pydantic import UUID4, BaseModel, field_validator, Field

class CountryRead(BaseModel):
    id: UUID4 = Field(...)
