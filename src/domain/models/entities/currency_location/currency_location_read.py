from pydantic import UUID4, BaseModel, field_validator, Field

class CurrencyLocationRead(BaseModel):
    id: UUID4 = Field(...)
