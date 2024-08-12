from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class PermissionSave(BaseModel):
    company_id: Optional[UUID4] = Field(default=None)
    name: str = Field(..., max_length=255)
    description: str = Field(default=None)
    state: bool = Field(default=True)
