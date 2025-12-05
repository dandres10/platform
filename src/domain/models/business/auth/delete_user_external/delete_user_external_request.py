from pydantic import BaseModel, Field, UUID4


class DeleteUserExternalRequest(BaseModel):
    user_id: UUID4 = Field(..., description="ID del usuario externo a eliminar")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

