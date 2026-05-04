from pydantic import BaseModel, field_validator, Field
from uuid import UUID

class RolPermissionDelete(BaseModel):
    id: UUID = Field(...)
