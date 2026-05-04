from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

class Rol(BaseModel):
    id: Optional[UUID] = Field(default=None)
    company_id: Optional[UUID] = Field(default=None)
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None)
    state: bool = Field(default=True)
    created_date: Optional[datetime] = Field(default_factory=datetime.now)
    updated_date: Optional[datetime] = Field(default_factory=datetime.now)

    def model_dump(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", set())
        exclude.update({"created_date", "updated_date"})
        return super().model_dump(*args, exclude=exclude, **kwargs)
