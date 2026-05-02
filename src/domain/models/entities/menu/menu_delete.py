from pydantic import BaseModel, field_validator, Field
from uuid import UUID

class MenuDelete(BaseModel):
    id: UUID = Field(...)
