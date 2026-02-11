from pydantic import BaseModel, Field
from uuid import UUID


class ChildrenByTypeRequest(BaseModel):
    parent_id: UUID = Field(...)
    type_name: str = Field(...)
