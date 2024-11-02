from pydantic import BaseModel, Field, UUID4
from typing import Optional
from datetime import datetime

class TranslationUpdate(BaseModel):
    id: UUID4 = Field(...)
    key: str = Field(..., max_length=255)
    language_code: str = Field(..., max_length=10)
    translation: str = Field(...)
    context: Optional[str] = Field(default=None, max_length=255)
    state: bool = Field(default=True)
