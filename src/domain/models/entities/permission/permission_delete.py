from pydantic import BaseModel, field_validator, Field
from uuid import UUID

class PermissionDelete(BaseModel):
    id: UUID = Field(...)
