from pydantic import BaseModel, Field
from uuid import UUID


class TypesByCountryRequest(BaseModel):
    country_id: UUID = Field(...)
