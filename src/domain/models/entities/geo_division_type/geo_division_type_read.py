from pydantic import UUID4, BaseModel, Field

class GeoDivisionTypeRead(BaseModel):
    id: UUID4 = Field(...)
