from pydantic import BaseModel, Field, UUID4, EmailStr
from typing import Optional
from datetime import datetime


class UserExternalItem(BaseModel):
    platform_id: UUID4 = Field(..., description="ID del platform")
    user_id: UUID4 = Field(..., description="ID del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    identification: str = Field(..., description="Documento de identificación")
    first_name: str = Field(..., description="Primer nombre")
    last_name: str = Field(..., description="Apellido")
    phone: Optional[str] = Field(None, description="Teléfono")
    user_state: bool = Field(..., description="Estado del usuario (activo/inactivo)")
    user_created_date: datetime = Field(..., description="Fecha de creación del usuario")
    user_updated_date: datetime = Field(..., description="Fecha de última actualización del usuario")
    language_id: UUID4 = Field(..., description="ID del idioma")
    currency_id: UUID4 = Field(..., description="ID de la moneda")
    token_expiration_minutes: int = Field(..., description="Minutos de expiración del token")
    refresh_token_expiration_minutes: int = Field(..., description="Minutos de expiración del refresh token")
    platform_created_date: datetime = Field(..., description="Fecha de creación del platform")
    platform_updated_date: datetime = Field(..., description="Fecha de última actualización del platform")

    class Config:
        json_schema_extra = {
            "example": {
                "platform_id": "ff0e8400-e29b-41d4-a716-446655440000",
                "user_id": "bb0e8400-e29b-41d4-a716-446655440000",
                "email": "carlos.ramirez@gmail.com",
                "identification": "98765432",
                "first_name": "Carlos",
                "last_name": "Ramírez",
                "phone": "+573009876543",
                "user_state": True,
                "user_created_date": "2024-03-20T15:45:00Z",
                "user_updated_date": "2024-03-20T15:45:00Z",
                "language_id": "550e8400-e29b-41d4-a716-446655440000",
                "currency_id": "770e8400-e29b-41d4-a716-446655440000",
                "token_expiration_minutes": 60,
                "refresh_token_expiration_minutes": 1440,
                "platform_created_date": "2024-03-20T15:45:00Z",
                "platform_updated_date": "2024-03-20T15:45:00Z"
            }
        }

