from pydantic import UUID4, BaseModel, field_validator, Field

class RolPermissionDelete(BaseModel):
    id: UUID4 = Field(...)
