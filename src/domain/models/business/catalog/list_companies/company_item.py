from typing import Optional
from pydantic import BaseModel, Field, UUID4


class CompanyItem(BaseModel):
    id: UUID4 = Field(..., description="ID de la empresa")
    name: str = Field(..., description="Nombre de la empresa")
    nit: str = Field(..., description="NIT de la empresa")
    state: bool = Field(..., description="Estado de la empresa (activa/inactiva)")
