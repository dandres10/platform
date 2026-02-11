from typing import Optional
from uuid import UUID
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.rol_type import ROL_TYPE
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.user_type_info import UserTypeInfo
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)


# Códigos de roles internos (ADMIN y COLLA son usuarios internos)
INTERNAL_ROL_CODES = [ROL_TYPE.ADMIN.value, ROL_TYPE.COLLA.value]


class CheckUserTypeByRolUseCase:
    """
    Use case para detectar el tipo de usuario basándose en el código del rol.
    
    El ROL es la marca irrefutable del tipo de usuario:
    - ADMIN, COLLA → Usuario INTERNO (tiene company, location)
    - USER → Usuario EXTERNO (no tiene company ni location)
    """
    
    def __init__(self):
        self.auth_repository = AuthRepository()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(self, config: Config, user_id: UUID) -> Optional[UserTypeInfo]:
        """
        Determina el tipo de usuario basándose en el código del rol.
        
        Args:
            config: Configuración de la solicitud
            user_id: ID del usuario a verificar
        
        Returns:
            UserTypeInfo con is_internal, rol_id y rol_code
            None si el usuario no tiene rol asignado (error)
        """
        # Obtener el rol del usuario desde user_location_rol
        user_rol = await self.auth_repository.get_user_rol_info(
            config=config, user_id=user_id
        )
        
        if user_rol is None:
            # Usuario sin rol asignado - esto no debería pasar
            return None
        
        # Determinar tipo basado en el código del rol
        is_internal = user_rol.rol_code in INTERNAL_ROL_CODES
        
        return UserTypeInfo(
            is_internal=is_internal,
            rol_id=user_rol.rol_id,
            rol_code=user_rol.rol_code
        )
