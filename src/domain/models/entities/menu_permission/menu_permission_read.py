from pydantic import UUID4, BaseModel, field_validator, Field

class MenuPermissionRead(BaseModel):
    id: UUID4 = Field(...)
