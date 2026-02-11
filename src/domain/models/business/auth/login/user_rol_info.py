from pydantic import BaseModel, Field, UUID4


class UserRolInfo(BaseModel):
    """Información básica del rol del usuario desde user_location_rol"""
    rol_id: UUID4 = Field(..., description="ID del rol")
    rol_code: str = Field(..., description="Código del rol")
