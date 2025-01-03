from pydantic import BaseModel, EmailStr, Field


class CompaniesByUser(BaseModel):
    email: EmailStr = Field(..., max_length=255)
