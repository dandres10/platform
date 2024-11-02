from pydantic import UUID4, BaseModel, field_validator, Field

class RolRead(BaseModel):
    id: UUID4 = Field(...)
