from pydantic import UUID4, BaseModel, Field

class GeoDivisionTypeDelete(BaseModel):
    id: UUID4 = Field(...)
