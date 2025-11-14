from pydantic import BaseModel, Field


class CreateUserExternalResponse(BaseModel):
    message: str = Field(...)

