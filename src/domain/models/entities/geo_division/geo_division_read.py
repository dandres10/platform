from pydantic import UUID4, BaseModel, Field

class GeoDivisionRead(BaseModel):
    id: UUID4 = Field(...)
