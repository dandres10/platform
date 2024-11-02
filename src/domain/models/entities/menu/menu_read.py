from pydantic import UUID4, BaseModel, field_validator, Field

class MenuRead(BaseModel):
    id: UUID4 = Field(...)
