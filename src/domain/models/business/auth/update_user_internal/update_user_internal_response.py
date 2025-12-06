from pydantic import BaseModel, Field


class UpdateUserInternalResponse(BaseModel):
    message: str = Field(...)

