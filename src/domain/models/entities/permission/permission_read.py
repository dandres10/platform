from pydantic import BaseModel, field_validator, Field
from uuid import UUID

class PermissionRead(BaseModel):
    id: UUID = Field(...)
