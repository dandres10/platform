from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class MenuPermissionSave(BaseModel):
    menu_id: Optional[UUID4] = Field(default=None)
    permission_id: Optional[UUID4] = Field(default=None)
    state: bool = Field(default=True)
