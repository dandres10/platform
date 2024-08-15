from pydantic import UUID4, BaseModel, field_validator, Field

class CurrencyDelete(BaseModel):
    id: UUID4 = Field(...)
