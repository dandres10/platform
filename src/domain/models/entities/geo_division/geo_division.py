from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class GeoDivision(BaseModel):
    id: Optional[UUID4] = Field(default=None)
    top_id: Optional[UUID4] = Field(default=None)
    geo_division_type_id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    code: Optional[str] = Field(default=None, max_length=20)
    phone_code: Optional[str] = Field(default=None, max_length=10)
    level: int = Field(default=0)
    state: bool = Field(default=True)
    created_date: Optional[datetime] = Field(default_factory=datetime.now)
    updated_date: Optional[datetime] = Field(default_factory=datetime.now)

    def dict(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", set())
        exclude.update({"created_date", "updated_date"})
        return super().model_dump(*args, exclude=exclude, **kwargs)
