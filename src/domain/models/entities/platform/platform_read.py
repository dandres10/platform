from pydantic import UUID4, BaseModel, field_validator, Field

class PlatformRead(BaseModel):
    id: UUID4 = Field(...)
