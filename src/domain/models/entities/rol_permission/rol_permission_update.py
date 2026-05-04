from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class RolPermissionUpdate(BaseModel):
    id: UUID = Field(...)
    rol_id: UUID = Field(...)
    permission_id: UUID = Field(...)
    state: bool = Field(default=True)
