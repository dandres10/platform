from pydantic import BaseModel, EmailStr, Field, UUID4, field_validator
from typing import Optional, List


class LocationRolItem(BaseModel):
    location_id: UUID4 = Field(..., description="ID de la ubicación")
    rol_id: UUID4 = Field(..., description="ID del rol")

    class Config:
        json_schema_extra = {
            "example": {
                "location_id": "660e8400-e29b-41d4-a716-446655440000",
                "rol_id": "880e8400-e29b-41d4-a716-446655440000"
            }
        }


class CreateUserInternalRequest(BaseModel):
    language_id: UUID4 = Field(..., description="ID del idioma del usuario")
    currency_id: UUID4 = Field(..., description="ID de la moneda")
    location_rol: List[LocationRolItem] = Field(
        ...,
        min_length=1,
        description="Lista de asignaciones de rol por ubicación (mínimo 1)"
    )
    email: EmailStr = Field(..., description="Email único del usuario")
    password: str = Field(..., min_length=8, max_length=255, description="Contraseña (será hasheada)")
    identification: str = Field(..., min_length=3, max_length=30, description="Documento de identificación")
    first_name: str = Field(..., min_length=2, max_length=100, description="Primer nombre")
    last_name: str = Field(..., min_length=2, max_length=100, description="Apellido")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono de contacto")
    token_expiration_minutes: Optional[int] = Field(default=60, ge=5, le=1440, description="Minutos de expiración del token")
    refresh_token_expiration_minutes: Optional[int] = Field(default=1440, ge=60, le=43200, description="Minutos de expiración del refresh token")

    @field_validator('location_rol')
    @classmethod
    def validate_no_exact_duplicates(cls, v: List[LocationRolItem]) -> List[LocationRolItem]:
        seen = set()
        for item in v:
            combination = (str(item.location_id), str(item.rol_id))
            if combination in seen:
                raise ValueError(
                    f"Combinación duplicada encontrada: location_id={item.location_id}, "
                    f"rol_id={item.rol_id}. No se permiten duplicados exactos."
                )
            seen.add(combination)
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "language_id": "550e8400-e29b-41d4-a716-446655440000",
                "currency_id": "770e8400-e29b-41d4-a716-446655440000",
                "location_rol": [
                    {
                        "location_id": "660e8400-e29b-41d4-a716-446655440000",
                        "rol_id": "880e8400-e29b-41d4-a716-446655440000"
                    },
                    {
                        "location_id": "660e8400-e29b-41d4-a716-446655440000",
                        "rol_id": "990e8400-e29b-41d4-a716-446655440000"
                    },
                    {
                        "location_id": "aa0e8400-e29b-41d4-a716-446655440000",
                        "rol_id": "bb0e8400-e29b-41d4-a716-446655440000"
                    }
                ],
                "email": "nuevo.usuario@goluti.com",
                "password": "SecurePassword123!",
                "identification": "12345678",
                "first_name": "Juan",
                "last_name": "Pérez",
                "phone": "+573001234567",
                "token_expiration_minutes": 60,
                "refresh_token_expiration_minutes": 1440
            }
        }

