from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class Menu(BaseModel):
    id: Optional[UUID4] = Field(default=None)
    company_id: Optional[UUID4] = Field(default=None)
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=300)
    top_id: Optional[UUID4] = Field(default=None)
    route: str = Field(..., max_length=300)
    state: bool = Field(default=True)
    icon: str = Field(..., max_length=50)
    created_date: Optional[datetime] = Field(default_factory=datetime.now)
    updated_date: Optional[datetime] = Field(default_factory=datetime.now)

    def dict(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", set())
        exclude.update({"created_date", "updated_date"})
        return super().model_dump(*args, exclude=exclude, **kwargs)
