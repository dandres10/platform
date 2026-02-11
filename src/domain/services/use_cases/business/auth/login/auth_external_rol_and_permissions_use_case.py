from typing import Union, Tuple, List
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.rol_type import ROL_TYPE
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.infrastructure.database.entities.rol_entity import RolEntity
from src.infrastructure.database.entities.permission_entity import PermissionEntity


class AuthExternalRolAndPermissionsUseCase:
    """
    Obtiene el rol USER y sus permisos para usuarios externos.
    
    Busca el rol por su código 'USER' en la tabla rol.
    """
    
    def __init__(self):
        self.auth_repository = AuthRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
    ) -> Union[
        Tuple[List[PermissionEntity], RolEntity],
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT

        result = await self.auth_repository.external_rol_and_permissions_by_code(
            config=config, rol_code=ROL_TYPE.USER.value
        )

        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND.value
                ),
            )

        # Extraer rol y permisos únicos
        permissions = []
        rol_entity = None
        seen_permission_ids = set()

        for rol, rol_permission, permission in result:
            if rol_entity is None:
                rol_entity = rol
            
            if permission.id not in seen_permission_ids:
                seen_permission_ids.add(permission.id)
                permissions.append(permission)

        return (permissions, rol_entity)
