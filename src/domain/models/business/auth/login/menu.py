from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional

# SPEC-027
class Menu(BaseModel):
    company: Optional[UUID] = Field(default=None)