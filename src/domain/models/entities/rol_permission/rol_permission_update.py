from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class RolPermissionUpdate(BaseModel):
    id: UUID4 = Field(...)
    rol_id: UUID4 = Field(...)
    permission_id: UUID4 = Field(...)
    state: bool = Field(default=True)
