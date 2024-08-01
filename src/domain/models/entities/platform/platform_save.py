from pydantic import UUID4, BaseModel, field_validator


class PlatformSave(BaseModel):
    language: UUID4

    """ @field_validator("language")
    def validate_language(cls, v):
        allowed_languages = {"en", "es", "fr"}  # Idiomas permitidos
        if v not in allowed_languages:
            raise ValueError(f"Language must be one of {allowed_languages}")
        return v """
