from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class Platform(BaseModel):
    id: Optional[UUID4] = Field(default=None)
    language_id: Optional[UUID4] = Field(default=None)
    location_id: Optional[UUID4] = Field(default=None)
    currency_location_id: Optional[UUID4] = Field(default=None)
    token_expiration_minutes: int = Field(default=None)
    refresh_token_expiration_minutes: int = Field(default=None)
    created_date: Optional[datetime] = Field(default_factory=datetime.now)
    updated_date: Optional[datetime] = Field(default_factory=datetime.now)

    def dict(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", set())
        exclude.update({"created_date", "updated_date"})
        return super().model_dump(*args, exclude=exclude, **kwargs)
