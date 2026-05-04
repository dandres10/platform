from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class RolPermissionSave(BaseModel):
    rol_id: Optional[UUID] = Field(default=None)
    permission_id: Optional[UUID] = Field(default=None)
    state: bool = Field(default=True)
