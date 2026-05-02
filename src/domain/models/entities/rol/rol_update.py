from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class RolUpdate(BaseModel):
    id: UUID = Field(...)
    company_id: UUID = Field(...)
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None)
    state: bool = Field(default=True)
