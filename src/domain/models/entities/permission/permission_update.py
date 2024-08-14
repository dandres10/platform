from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class PermissionUpdate(BaseModel):
    id: UUID4 = Field(...)
    company_id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    description: str = Field(default=None)
    state: bool = Field(default=True)
