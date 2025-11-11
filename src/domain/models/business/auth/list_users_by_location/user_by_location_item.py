from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, UUID4


class UserByLocationItem(BaseModel):
    user_location_rol_id: UUID4 = Field(..., description="ID de la asignación user-location-rol")
    location_id: UUID4 = Field(..., description="ID de la ubicación")
    user_id: UUID4 = Field(..., description="ID del usuario")
    email: str = Field(..., description="Email del usuario")
    identification: str = Field(..., description="Identificación del usuario")
    first_name: str = Field(..., description="Primer nombre del usuario")
    last_name: str = Field(..., description="Apellido del usuario")
    phone: Optional[str] = Field(None, description="Teléfono del usuario")
    user_state: bool = Field(..., description="Estado del usuario (activo/inactivo)")
    user_created_date: datetime = Field(..., description="Fecha de creación del usuario")
    user_updated_date: datetime = Field(..., description="Fecha de última actualización del usuario")
    rol_id: UUID4 = Field(..., description="ID del rol")
    rol_name: str = Field(..., description="Nombre del rol")
    rol_code: str = Field(..., description="Código del rol")
    rol_description: Optional[str] = Field(None, description="Descripción del rol")

    class Config:
        json_schema_extra = {
            "example": {
                "user_location_rol_id": "123e4567-e89b-12d3-a456-426614174000",
                "location_id": "660e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "juan.perez@goluti.com",
                "identification": "12345678",
                "first_name": "Juan",
                "last_name": "Pérez",
                "phone": "+573001234567",
                "user_state": True,
                "user_created_date": "2024-01-15T10:30:00Z",
                "user_updated_date": "2024-01-15T10:30:00Z",
                "rol_id": "770e8400-e29b-41d4-a716-446655440000",
                "rol_name": "Administrador",
                "rol_code": "ADMIN",
                "rol_description": "Administrador del sistema"
            }
        }

