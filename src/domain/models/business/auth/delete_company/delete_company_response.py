from pydantic import BaseModel, Field


class DeleteCompanyResponse(BaseModel):
    message: str = Field(...)

