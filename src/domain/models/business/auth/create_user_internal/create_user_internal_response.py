from pydantic import BaseModel, Field


class CreateUserInternalResponse(BaseModel):
    message: str = Field(...)

