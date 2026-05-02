from pydantic import BaseModel, Field
from uuid import UUID

class GeoDivisionRead(BaseModel):
    id: UUID = Field(...)
