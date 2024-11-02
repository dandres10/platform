from typing import List, Tuple, Union
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_login_response import (
    PermissionLoginResponse,
)
from src.domain.models.business.auth.login.auth_user_role_and_permissions import (
    AuthUserRoleAndPermissions,
)
from src.infrastructure.database.entities.rol_entity import RolEntity
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.core.config import settings
from src.infrastructure.database.repositories.business.mappers.auth.login.login_mapper import (
    map_to_permission_response,
)
from src.core.classes.async_message import Message


class AuthUserRoleAndPermissionsUseCase:
    def __init__(
        self,
    ):
        self.auth_repository = AuthRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: AuthUserRoleAndPermissions,
    ) -> Union[
        Tuple[
            list[PermissionLoginResponse],
            RolEntity,
        ],
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT
        permissions: List[PermissionLoginResponse] = []
        results = await self.auth_repository.user_role_and_permissions(
            config=config,
            params=params,
        )

        if not results:
            print("no se encontro informacion relacionada rol y permisos")
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        for user_role_and_permission in results:
            user_location_rol_q, user_q, rol_q, rol_permission_q, permission_q = (
                user_role_and_permission
            )
            permissions.append(
                map_to_permission_response(permission_entity=permission_q)
            )

        return (permissions, rol_q)
