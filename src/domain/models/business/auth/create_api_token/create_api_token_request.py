from pydantic import UUID4, BaseModel, Field


class CreateApiTokenRequest(BaseModel):
    rol_id: UUID4 = Field(...)
