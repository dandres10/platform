from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class GeoDivisionHierarchyItemResponse(BaseModel):
    id: UUID = Field(...)
    name: str = Field(...)
    code: Optional[str] = Field(default=None)
    phone_code: Optional[str] = Field(default=None)
    level: int = Field(...)
    type: str = Field(...)
    type_label: str = Field(...)


class GeoDivisionHierarchyResponse(BaseModel):
    node: GeoDivisionHierarchyItemResponse = Field(...)
    ancestors: List[GeoDivisionHierarchyItemResponse] = Field(...)
    depth: int = Field(...)
