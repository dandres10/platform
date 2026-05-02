from pydantic import BaseModel, field_validator, Field
from uuid import UUID

class RolPermissionRead(BaseModel):
    id: UUID = Field(...)
