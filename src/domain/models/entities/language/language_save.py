from typing import Optional
from pydantic import UUID4, BaseModel, field_validator, Field


class LanguageSave(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=10)
    native_name: Optional[str] = Field(None, max_length=100)
    state: bool = Field(default=True)

    @field_validator('name')
    def validate_name(cls, v):
        if len(v) > 100:
            raise ValueError('Name must be 100 characters or fewer')
        return v

    @field_validator('code')
    def validate_code(cls, v):
        if len(v) > 10:
            raise ValueError('Code must be 10 characters or fewer')
        return v
    
    @field_validator('native_name')
    def validate_native_name(cls, v):
        if len(v) > 100:
            raise ValueError('Native name must be 100 characters or fewer')
        return v
