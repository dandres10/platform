from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class GeoDivisionSave(BaseModel):
    top_id: Optional[UUID] = Field(default=None)
    geo_division_type_id: UUID = Field(...)
    name: str = Field(..., max_length=255)
    code: Optional[str] = Field(default=None, max_length=20)
    phone_code: Optional[str] = Field(default=None, max_length=10)
    level: int = Field(default=0)
    state: bool = Field(default=True)
