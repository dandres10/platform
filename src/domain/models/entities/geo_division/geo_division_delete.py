from pydantic import BaseModel, Field
from uuid import UUID

class GeoDivisionDelete(BaseModel):
    id: UUID = Field(...)
