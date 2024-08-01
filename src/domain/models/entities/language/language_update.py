from typing import Optional
from datetime import datetime
from pydantic import UUID4, BaseModel, field_validator, Field


class LanguageUpdate(BaseModel):
    id: Optional[UUID4] = Field(default=None)
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)
    native_name: Optional[str] = Field(None, max_length=100)
    state: bool = Field(default=True)
