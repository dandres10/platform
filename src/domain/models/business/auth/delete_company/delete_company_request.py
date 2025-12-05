from pydantic import BaseModel, Field, UUID4


class DeleteCompanyRequest(BaseModel):
    company_id: UUID4 = Field(..., description="ID de la compañía a eliminar")

    class Config:
        json_schema_extra = {
            "example": {
                "company_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }

