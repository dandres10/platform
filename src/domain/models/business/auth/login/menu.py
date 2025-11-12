from pydantic import UUID4, BaseModel, Field
from typing import Optional

class Menu(BaseModel):
    company: Optional[UUID4] = Field(default=None)