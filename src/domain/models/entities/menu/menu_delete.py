from pydantic import UUID4, BaseModel, field_validator, Field

class MenuDelete(BaseModel):
    id: UUID4 = Field(...)
