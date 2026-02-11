from pydantic import BaseModel, Field
from uuid import UUID


class ByCountryAndTypeRequest(BaseModel):
    country_id: UUID = Field(...)
    type_name: str = Field(...)
