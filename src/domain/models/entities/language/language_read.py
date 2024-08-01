from typing import Optional
from datetime import datetime
from pydantic import UUID4, BaseModel, field_validator, Field


class LanguageRead(BaseModel):
    id: UUID4 = Field(...)
