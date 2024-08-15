from pydantic import UUID4, BaseModel, field_validator, Field

class CompanyRead(BaseModel):
    id: UUID4 = Field(...)
