from pydantic import UUID4, BaseModel, field_validator, Field

class CompanyDelete(BaseModel):
    id: UUID4 = Field(...)
