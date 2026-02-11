from pydantic import UUID4, BaseModel, Field

class GeoDivisionDelete(BaseModel):
    id: UUID4 = Field(...)
