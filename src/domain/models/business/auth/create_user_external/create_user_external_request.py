from pydantic import BaseModel, EmailStr, Field, UUID4
from typing import Optional


class CreateUserExternalRequest(BaseModel):
    language_id: UUID4 = Field(..., description="ID del idioma del usuario")
    currency_id: UUID4 = Field(..., description="ID de la moneda")
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=8, max_length=255, description="Contraseña (será hasheada)")
    identification: str = Field(..., min_length=3, max_length=30, description="Documento de identificación único")
    first_name: str = Field(..., min_length=2, max_length=100, description="Primer nombre")
    last_name: str = Field(..., min_length=2, max_length=100, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    token_expiration_minutes: Optional[int] = Field(default=60, ge=5, le=1440, description="Minutos de expiración del token")
    refresh_token_expiration_minutes: Optional[int] = Field(default=1440, ge=60, le=43200, description="Minutos de expiración del refresh token")

    class Config:
        json_schema_extra = {
            "example": {
                "language_id": "550e8400-e29b-41d4-a716-446655440000",
                "currency_id": "770e8400-e29b-41d4-a716-446655440000",
                "email": "usuario@example.com",
                "password": "SecurePassword123!",
                "identification": "12345678",
                "first_name": "Juan",
                "last_name": "Pérez",
                "phone": "+573001234567",
                "token_expiration_minutes": 60,
                "refresh_token_expiration_minutes": 1440
            }
        }

