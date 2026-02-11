from pydantic import BaseModel, Field, UUID4


class UserTypeInfo(BaseModel):
    """Información del tipo de usuario basada en su rol"""
    is_internal: bool = Field(..., description="True si es usuario interno (ADMIN/COLLA), False si es externo (USER)")
    rol_id: UUID4 = Field(..., description="ID del rol del usuario")
    rol_code: str = Field(..., description="Código del rol (ADMIN, COLLA, USER)")
