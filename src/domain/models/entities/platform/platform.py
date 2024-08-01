from datetime import datetime
from typing import Optional
from dataclasses import field

from pydantic import UUID4, BaseModel, field_validator


class Platform(BaseModel):
    language: UUID4
    created_date: datetime
    updated_date: datetime
    id: Optional[UUID4] = field(default=None)

    """ @field_validator("language")
    def validate_language(cls, v):
        allowed_languages = {"en", "es", "fr"}  # Idiomas permitidos
        if v not in allowed_languages:
            raise ValueError(f"Language must be one of {allowed_languages}")
        return v """
