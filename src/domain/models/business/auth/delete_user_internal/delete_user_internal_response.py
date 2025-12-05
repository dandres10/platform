from pydantic import BaseModel, Field


class DeleteUserInternalResponse(BaseModel):
    message: str = Field(...)

