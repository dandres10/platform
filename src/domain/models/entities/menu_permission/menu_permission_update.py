from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class MenuPermissionUpdate(BaseModel):
    id: UUID = Field(...)
    menu_id: UUID = Field(...)
    permission_id: UUID = Field(...)
    state: bool = Field(default=True)
