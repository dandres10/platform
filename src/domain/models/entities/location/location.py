from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class Location(BaseModel):
    id: Optional[UUID4] = Field(default=None)
    company_id: Optional[UUID4] = Field(default=None)
    country_id: Optional[UUID4] = Field(default=None)
    city_id: Optional[UUID] = Field(default=None)  # UUID genérico (acepta UUIDs fijos de geo_division)
    name: str = Field(..., max_length=255)
    address: str = Field(...)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=100)
    main_location: bool = Field(default=False)
    latitude: Optional[Decimal] = Field(default=None)
    longitude: Optional[Decimal] = Field(default=None)
    google_place_id: Optional[str] = Field(default=None, max_length=255)
    state: bool = Field(default=True)
    created_date: Optional[datetime] = Field(default_factory=datetime.now)
    updated_date: Optional[datetime] = Field(default_factory=datetime.now)

    def dict(self, *args, **kwargs):
        exclude = kwargs.pop("exclude", set())
        exclude.update({"created_date", "updated_date"})
        return super().model_dump(*args, exclude=exclude, **kwargs)
