from pydantic import BaseModel, EmailStr, Field


class AuthInitialUserData(BaseModel):
    email: EmailStr = Field(..., max_length=255)
