from pydantic import BaseModel, field_validator, Field
from uuid import UUID

class MenuPermissionDelete(BaseModel):
    id: UUID = Field(...)
