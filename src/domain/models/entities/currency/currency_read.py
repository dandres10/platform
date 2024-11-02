from pydantic import UUID4, BaseModel, field_validator, Field

class CurrencyRead(BaseModel):
    id: UUID4 = Field(...)
