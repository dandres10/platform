from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class MenuUpdate(BaseModel):
    id: UUID4 = Field(...)
    company_id: Optional[UUID4] = Field(default=None)
    name: str = Field(..., max_length=100)
    label: str = Field(..., max_length=300)
    description: str = Field(..., max_length=300)
    top_id: UUID4 = Field(...)
    route: str = Field(..., max_length=300)
    state: bool = Field(default=True)
    icon: str = Field(..., max_length=50)
