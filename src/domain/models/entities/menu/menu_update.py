from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class MenuUpdate(BaseModel):
    id: UUID = Field(...)
    company_id: Optional[UUID] = Field(default=None)
    name: str = Field(..., max_length=100)
    label: str = Field(..., max_length=300)
    description: str = Field(..., max_length=300)
    top_id: UUID = Field(...)
    route: str = Field(..., max_length=300)
    state: bool = Field(default=True)
    icon: str = Field(..., max_length=50)
    type: str = Field(default="INTERNAL", max_length=20)
