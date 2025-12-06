from pydantic import BaseModel, Field, UUID4
from typing import Optional


class UpdateUserInternalRequest(BaseModel):
    password: Optional[str] = Field(None, max_length=255, description="Nueva contraseña (será hasheada)")
    email: Optional[str] = Field(None, max_length=255, description="Email del usuario")
    identification: Optional[str] = Field(None, max_length=30, description="Documento de identificación")
    first_name: Optional[str] = Field(None, max_length=255, description="Primer nombre")
    last_name: Optional[str] = Field(None, max_length=255, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    state: Optional[bool] = Field(None, description="Estado del usuario (activo/inactivo)")
    rol_id: Optional[UUID4] = Field(None, description="Nuevo rol para el usuario en la ubicación")

    class Config:
        json_schema_extra = {
            "example": {
                "password": "NewSecurePassword123!",
                "email": "usuario@goluti.com",
                "identification": "12345678",
                "first_name": "Juan",
                "last_name": "Pérez García",
                "phone": "+573001234567",
                "state": True,
                "rol_id": "880e8400-e29b-41d4-a716-446655440000"
            }
        }

