from pydantic import UUID4, BaseModel, field_validator, Field

class LocationDelete(BaseModel):
    id: UUID4 = Field(...)
