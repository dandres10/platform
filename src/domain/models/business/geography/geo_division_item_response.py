from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class GeoDivisionItemResponse(BaseModel):
    id: UUID = Field(...)
    name: str = Field(...)
    code: Optional[str] = Field(default=None)
    phone_code: Optional[str] = Field(default=None)
    level: int = Field(...)
    type: str = Field(...)
    type_label: str = Field(...)
