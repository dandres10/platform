from pydantic import UUID4, BaseModel, field_validator, Field

class CompanyCurrencyRead(BaseModel):
    id: UUID4 = Field(...)
