from pydantic import UUID4, BaseModel, field_validator, Field

class UserCountryDelete(BaseModel):
    id: UUID4 = Field(...)
