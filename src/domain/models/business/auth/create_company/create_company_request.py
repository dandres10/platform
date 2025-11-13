from pydantic import BaseModel, Field, UUID4, EmailStr
from typing import Optional


class CompanyData(BaseModel):
    """Datos de la compañía a crear"""
    name: str = Field(..., min_length=3, max_length=255, description="Nombre de la compañía")
    nit: str = Field(..., min_length=5, max_length=255, description="NIT de la compañía")
    inactivity_time: int = Field(default=30, ge=1, le=1440, description="Tiempo de inactividad en minutos")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Empresa Ejemplo S.A.S.",
                "nit": "900123456-7",
                "inactivity_time": 30
            }
        }


class LocationData(BaseModel):
    """Datos de la ubicación principal"""
    country_id: UUID4 = Field(..., description="ID del país")
    name: str = Field(..., min_length=3, max_length=255, description="Nombre de la ubicación")
    address: str = Field(..., min_length=5, description="Dirección completa")
    city: str = Field(..., min_length=2, max_length=100, description="Ciudad")
    phone: str = Field(..., min_length=7, max_length=20, description="Teléfono")
    email: EmailStr = Field(..., description="Email de contacto de la ubicación")

    class Config:
        json_schema_extra = {
            "example": {
                "country_id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "Sede Principal",
                "address": "Calle 123 #45-67",
                "city": "Bogotá",
                "phone": "+57 300 1234567",
                "email": "contacto@empresaejemplo.com"
            }
        }


class AdminUserData(BaseModel):
    """Datos del usuario administrador inicial"""
    email: EmailStr = Field(..., description="Email del usuario (login)")
    password: str = Field(..., min_length=8, max_length=100, description="Contraseña")
    first_name: str = Field(..., min_length=2, max_length=100, description="Nombre(s)")
    last_name: str = Field(..., min_length=2, max_length=100, description="Apellido(s)")
    identification: str = Field(..., min_length=5, max_length=50, description="Número de identificación")
    phone: str = Field(..., min_length=7, max_length=20, description="Teléfono")
    language_id: UUID4 = Field(..., description="ID del idioma preferido")
    currency_id: UUID4 = Field(..., description="ID de la moneda preferida")
    rol_id: UUID4 = Field(..., description="ID del rol (debe ser rol de administrador)")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "admin@empresaejemplo.com",
                "password": "SecureP@ssw0rd123!",
                "first_name": "Juan",
                "last_name": "Pérez",
                "identification": "1234567890",
                "phone": "+57 300 9876543",
                "language_id": "660e8400-e29b-41d4-a716-446655440000",
                "currency_id": "770e8400-e29b-41d4-a716-446655440000",
                "rol_id": "880e8400-e29b-41d4-a716-446655440000"
            }
        }


class CreateCompanyRequest(BaseModel):
    """Request completo para crear una compañía"""
    company: CompanyData = Field(..., description="Datos de la compañía")
    location: LocationData = Field(..., description="Datos de la ubicación principal")
    admin_user: AdminUserData = Field(..., description="Datos del usuario administrador")

    class Config:
        json_schema_extra = {
            "example": {
                "company": {
                    "name": "Empresa Ejemplo S.A.S.",
                    "nit": "900123456-7",
                    "inactivity_time": 30
                },
                "location": {
                    "country_id": "550e8400-e29b-41d4-a716-446655440000",
                    "name": "Sede Principal",
                    "address": "Calle 123 #45-67",
                    "city": "Bogotá",
                    "phone": "+57 300 1234567",
                    "email": "contacto@empresaejemplo.com"
                },
                "admin_user": {
                    "email": "admin@empresaejemplo.com",
                    "password": "SecureP@ssw0rd123!",
                    "first_name": "Juan",
                    "last_name": "Pérez",
                    "identification": "1234567890",
                    "phone": "+57 300 9876543",
                    "language_id": "660e8400-e29b-41d4-a716-446655440000",
                    "currency_id": "770e8400-e29b-41d4-a716-446655440000",
                    "rol_id": "880e8400-e29b-41d4-a716-446655440000"
                }
            }
        }

