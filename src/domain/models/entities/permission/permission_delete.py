from pydantic import UUID4, BaseModel, field_validator, Field

class PermissionDelete(BaseModel):
    id: UUID4 = Field(...)
