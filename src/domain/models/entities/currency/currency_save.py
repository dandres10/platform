from pydantic import BaseModel, UUID4, Field, field_validator
from typing import Optional
from datetime import datetime


class CurrencySave(BaseModel):
    name: str = Field(..., max_length=255)
    code: str = Field(..., max_length=10)
    symbol: str = Field(..., max_length=10)
    state: bool = Field(default=True)

    @field_validator("name")
    def validate_name(cls, v):
        if len(v) > 255:
            raise ValueError("Name must be 100 characters or fewer")
        return v

    @field_validator("code")
    def validate_code(cls, v):
        if len(v) > 10:
            raise ValueError("Code must be 10 characters or fewer")
        return v

    @field_validator("symbol")
    def validate_symbol(cls, v):
        if len(v) > 10:
            raise ValueError("Symbol name must be 10 characters or fewer")
        return v
