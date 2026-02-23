from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, UUID4


class LocationItem(BaseModel):
    id: UUID4 = Field(..., description="ID de la ubicacion/sucursal")
    company_id: Optional[UUID4] = Field(None, description="ID de la empresa")
    name: str = Field(..., description="Nombre de la sucursal")
    address: str = Field(..., description="Direccion de la sucursal")
    phone: str = Field(..., description="Telefono de la sucursal")
    email: str = Field(..., description="Email de la sucursal")
    main_location: bool = Field(..., description="Si es la sucursal principal")
    country_id: Optional[UUID4] = Field(None, description="ID del pais")
    city_id: Optional[UUID] = Field(None, description="ID de la ciudad")
    latitude: Optional[Decimal] = Field(None, description="Latitud")
    longitude: Optional[Decimal] = Field(None, description="Longitud")
    state: bool = Field(..., description="Estado de la sucursal (activa/inactiva)")
