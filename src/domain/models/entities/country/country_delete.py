from pydantic import UUID4, BaseModel, field_validator, Field

class CountryDelete(BaseModel):
    id: UUID4 = Field(...)
