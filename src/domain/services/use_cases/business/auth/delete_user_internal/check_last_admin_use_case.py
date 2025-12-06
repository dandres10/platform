from typing import Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.rol_type import ROL_TYPE
from src.core.models.config import Config
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.wrappers.execute_transaction import execute_transaction

from src.domain.services.use_cases.entities.rol.rol_list_use_case import (
    RolListUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_list_use_case import (
    UserLocationRolListUseCase
)

from src.infrastructure.database.repositories.entities.rol_repository import (
    RolRepository
)
from src.infrastructure.database.repositories.entities.user_location_rol_repository import (
    UserLocationRolRepository
)


rol_repository = RolRepository()
user_location_rol_repository = UserLocationRolRepository()


class CheckLastAdminUseCase:
    """
    Verifica si un usuario es el último administrador en una ubicación.
    Si el usuario tiene rol ADMIN y es el único en la ubicación, no puede ser eliminado.
    """
    
    def __init__(self):
        self.rol_list_uc = RolListUseCase(rol_repository)
        self.user_location_rol_list_uc = UserLocationRolListUseCase(user_location_rol_repository)

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        user_id: UUID4,
        location_id: UUID4,
        user_location_rols: list
    ) -> bool:
        """
        Verifica si el usuario es el último administrador en la ubicación.
        
        Args:
            config: Configuración de la petición
            user_id: ID del usuario a verificar
            location_id: ID de la ubicación del admin que ejecuta la acción
            user_location_rols: Lista de user_location_rol del usuario a eliminar
            
        Returns:
            bool: True si es el último admin (no puede eliminarse), False si puede eliminarse
        """
        # Obtener el rol ADMIN
        admin_roles = await self.rol_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="code",
                        condition=CONDITION_TYPE.EQUALS,
                        value=ROL_TYPE.ADMIN.value
                    )
                ]
            )
        )
        
        # Si no se puede obtener el rol ADMIN, permitir continuar
        if not admin_roles or isinstance(admin_roles, str) or len(admin_roles) == 0:
            return False
        
        admin_rol_id = str(admin_roles[0].id)
        location_id_str = str(location_id)
        
        # Verificar si el usuario a eliminar tiene rol ADMIN en esta ubicación
        user_has_admin_role = False
        for ulr in user_location_rols:
            if str(ulr.location_id) == location_id_str and str(ulr.rol_id) == admin_rol_id:
                user_has_admin_role = True
                break
        
        # Si el usuario no tiene rol ADMIN, puede eliminarse
        if not user_has_admin_role:
            return False
        
        # Obtener todos los user_location_rols con rol ADMIN en esta ubicación
        admins_in_location = await self.user_location_rol_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="location_id",
                        condition=CONDITION_TYPE.EQUALS,
                        value=location_id_str
                    ),
                    FilterManager(
                        field="rol_id",
                        condition=CONDITION_TYPE.EQUALS,
                        value=admin_rol_id
                    )
                ],
                all_data=True
            )
        )
        
        # Si solo hay un admin y es el usuario a eliminar, no permitir
        if admins_in_location and not isinstance(admins_in_location, str):
            if len(admins_in_location) <= 1:
                return True  # Es el último admin, no puede eliminarse
        
        return False  # Hay más admins, puede eliminarse

