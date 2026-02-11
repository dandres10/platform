from pydantic import BaseModel, Field
from uuid import UUID


class DetailRequest(BaseModel):
    node_id: UUID = Field(...)
