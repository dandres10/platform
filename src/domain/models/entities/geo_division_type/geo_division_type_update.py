from pydantic import BaseModel, Field, UUID4
from typing import Optional

class GeoDivisionTypeUpdate(BaseModel):
    id: UUID4 = Field(...)
    name: str = Field(..., max_length=50)
    label: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None)
    state: bool = Field(default=True)
