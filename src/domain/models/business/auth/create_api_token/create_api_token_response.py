from typing import List
from pydantic import UUID4, BaseModel, Field


class CreateApiTokenResponse(BaseModel):
    rol_id: UUID4 = Field(...)
    rol_code: str = Field(...)
    permissions: List[str] = Field(...)
