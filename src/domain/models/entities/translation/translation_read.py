from pydantic import UUID4, BaseModel, field_validator, Field

class TranslationRead(BaseModel):
    id: UUID4 = Field(...)
