from decimal import Decimal
from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class LocationUpdate(BaseModel):
    id: UUID4 = Field(...)
    company_id: UUID4 = Field(...)
    country_id: UUID4 = Field(...)
    city_id: Optional[UUID4] = Field(default=None)
    name: str = Field(..., max_length=255)
    address: str = Field(...)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=100)
    main_location: bool = Field(default=False)
    latitude: Optional[Decimal] = Field(default=None)
    longitude: Optional[Decimal] = Field(default=None)
    google_place_id: Optional[str] = Field(default=None, max_length=255)
    state: bool = Field(default=True)
