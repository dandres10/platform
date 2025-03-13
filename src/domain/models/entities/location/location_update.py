from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class LocationUpdate(BaseModel):
    id: UUID4 = Field(...)
    company_id: UUID4 = Field(...)
    country_id: UUID4 = Field(...)
    name: str = Field(..., max_length=255)
    address: str = Field(...)
    city: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=100)
    main_location: bool = Field(default=False)
    state: bool = Field(default=True)
