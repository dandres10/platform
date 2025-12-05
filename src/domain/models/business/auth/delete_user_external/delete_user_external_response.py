from pydantic import BaseModel, Field


class DeleteUserExternalResponse(BaseModel):
    message: str = Field(...)

