from pydantic import BaseModel, field_validator, Field
from uuid import UUID

class MenuRead(BaseModel):
    id: UUID = Field(...)
