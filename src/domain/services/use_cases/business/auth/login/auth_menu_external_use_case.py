from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_login_response import MenuLoginResponse
from src.infrastructure.database.repositories.business.auth_repository import AuthRepository
from src.infrastructure.database.repositories.business.mappers.auth.login.login_mapper import (
    map_to_menu_response,
)


class AuthMenuExternalUseCase:
    """
    Obtiene los menús para usuarios externos.
    
    Solo retorna menús con type='EXTERNAL' que estén asociados
    a los permisos del rol USER.
    """
    
    def __init__(self):
        self.auth_repository = AuthRepository()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        permissions: list,  # Lista de PermissionEntity del rol USER
    ) -> Union[List[MenuLoginResponse], str]:
        config.response_type = RESPONSE_TYPE.OBJECT

        # Obtener IDs de permisos
        permission_ids = [str(p.id) for p in permissions]

        # Obtener menús externos filtrados por permisos
        menus = await self.auth_repository.menu_external(
            config=config, permission_ids=permission_ids
        )

        if not menus:
            return []  # Retornar lista vacía, no error

        # Extraer y mapear menús únicos
        seen_menu_ids = set()
        result = []
        
        for menu_permission, menu_entity in menus:
            if menu_entity.id not in seen_menu_ids:
                seen_menu_ids.add(menu_entity.id)
                result.append(map_to_menu_response(menu_entity=menu_entity))

        return result
