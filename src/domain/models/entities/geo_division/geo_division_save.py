from pydantic import BaseModel, Field, UUID4
from typing import Optional

class GeoDivisionSave(BaseModel):
    top_id: Optional[UUID4] = Field(default=None)
    geo_division_type_id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    code: Optional[str] = Field(default=None, max_length=20)
    phone_code: Optional[str] = Field(default=None, max_length=10)
    level: int = Field(default=0)
    state: bool = Field(default=True)
