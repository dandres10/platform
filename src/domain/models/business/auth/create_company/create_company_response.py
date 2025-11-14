from pydantic import BaseModel, Field


class CreateCompanyResponse(BaseModel):
    message: str = Field(...)

