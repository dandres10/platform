from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class CompanyCurrency(BaseModel):
    id: Optional[UUID4] = Field(default=None)
    company_id: Optional[UUID4] = Field(default=None)
    currency_id: Optional[UUID4] = Field(default=None)
    is_base: bool = Field(default=False)
    state: bool = Field(default=True)
    created_date: Optional[datetime] = Field(default_factory=datetime.now)
    updated_date: Optional[datetime] = Field(default_factory=datetime.now)

    def dict(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", set())
        exclude.update({"created_date", "updated_date"})
        return super().model_dump(*args, exclude=exclude, **kwargs)
