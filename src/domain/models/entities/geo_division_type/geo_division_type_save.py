from pydantic import BaseModel, Field
from typing import Optional

class GeoDivisionTypeSave(BaseModel):
    name: str = Field(..., max_length=50)
    label: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None)
    state: bool = Field(default=True)
