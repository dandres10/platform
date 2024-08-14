from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class LocationSave(BaseModel):
    company_id: Optional[UUID4] = Field(default=None)
    country_id: Optional[UUID4] = Field(default=None)
    name: str = Field(..., max_length=255)
    address: str = Field(default=None)
    city: str = Field(..., max_length=100)
    phone: str = Field(..., max_length=20)
    email: str = Field(..., max_length=100)
    main_location: bool = Field(default=False)
    state: bool = Field(default=True)
