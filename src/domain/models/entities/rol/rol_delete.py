from pydantic import UUID4, BaseModel, field_validator, Field

class RolDelete(BaseModel):
    id: UUID4 = Field(...)
