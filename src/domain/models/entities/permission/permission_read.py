from pydantic import UUID4, BaseModel, field_validator, Field

class PermissionRead(BaseModel):
    id: UUID4 = Field(...)
