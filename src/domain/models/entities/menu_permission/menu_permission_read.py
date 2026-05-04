from pydantic import BaseModel, field_validator, Field
from uuid import UUID

class MenuPermissionRead(BaseModel):
    id: UUID = Field(...)
