from pydantic import BaseModel, Field
from uuid import UUID


class HierarchyRequest(BaseModel):
    node_id: UUID = Field(...)
