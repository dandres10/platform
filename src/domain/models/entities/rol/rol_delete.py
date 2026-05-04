from pydantic import BaseModel, field_validator, Field
from uuid import UUID

class RolDelete(BaseModel):
    id: UUID = Field(...)
