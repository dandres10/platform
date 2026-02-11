from pydantic import BaseModel, Field
from uuid import UUID


class GeoDivisionTypeByCountryResponse(BaseModel):
    id: UUID = Field(...)
    name: str = Field(...)
    label: str = Field(...)
    level: int = Field(...)
    count: int = Field(...)
