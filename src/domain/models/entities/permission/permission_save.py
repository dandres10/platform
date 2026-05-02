from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class PermissionSave(BaseModel):
    company_id: Optional[UUID] = Field(default=None)
    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None)
    state: bool = Field(default=True)
