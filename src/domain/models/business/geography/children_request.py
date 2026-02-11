from pydantic import BaseModel, Field
from uuid import UUID


class ChildrenRequest(BaseModel):
    parent_id: UUID = Field(...)
