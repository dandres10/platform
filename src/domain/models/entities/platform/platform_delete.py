from pydantic import UUID4, BaseModel, field_validator, Field

class PlatformDelete(BaseModel):
    id: UUID4 = Field(...)
