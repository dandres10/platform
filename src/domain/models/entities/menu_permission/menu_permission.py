from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

# SPEC-027
class MenuPermission(BaseModel):
    id: Optional[UUID] = Field(default=None)
    menu_id: Optional[UUID] = Field(default=None)
    permission_id: Optional[UUID] = Field(default=None)
    state: bool = Field(default=True)
    created_date: Optional[datetime] = Field(default_factory=datetime.now)
    updated_date: Optional[datetime] = Field(default_factory=datetime.now)

    def dict(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", set())
        exclude.update({"created_date", "updated_date"})
        return super().model_dump(*args, exclude=exclude, **kwargs)
