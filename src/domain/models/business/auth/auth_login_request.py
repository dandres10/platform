from pydantic import BaseModel


from pydantic import BaseModel, Field, EmailStr


class AuthLoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
