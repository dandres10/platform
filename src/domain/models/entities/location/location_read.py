from pydantic import UUID4, BaseModel, field_validator, Field

class LocationRead(BaseModel):
    id: UUID4 = Field(...)
