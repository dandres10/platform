from pydantic import UUID4, BaseModel, field_validator, Field

class MenuPermissionDelete(BaseModel):
    id: UUID4 = Field(...)
