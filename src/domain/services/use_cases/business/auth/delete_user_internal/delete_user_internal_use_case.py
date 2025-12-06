from typing import Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.business.auth.delete_user_internal import (
    DeleteUserInternalRequest
)
from src.domain.models.entities.user.index import UserRead, UserDelete
from src.domain.models.entities.user_location_rol.index import UserLocationRolDelete
from src.domain.models.entities.platform.index import PlatformDelete

from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase
)
from src.domain.services.use_cases.entities.user.user_delete_use_case import (
    UserDeleteUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_list_use_case import (
    UserLocationRolListUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_delete_use_case import (
    UserLocationRolDeleteUseCase
)
from src.domain.services.use_cases.entities.platform.platform_delete_use_case import (
    PlatformDeleteUseCase
)

from .check_active_relations_use_case import CheckActiveRelationsUseCase
from .check_last_admin_use_case import CheckLastAdminUseCase
from .soft_delete_user_use_case import SoftDeleteUserUseCase

from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)
from src.infrastructure.database.repositories.entities.user_location_rol_repository import (
    UserLocationRolRepository
)
from src.infrastructure.database.repositories.entities.platform_repository import (
    PlatformRepository
)


user_repository = UserRepository()
user_location_rol_repository = UserLocationRolRepository()
platform_repository = PlatformRepository()


class DeleteUserInternalUseCase:
    def __init__(self):
        self.user_read_uc = UserReadUseCase(user_repository)
        self.user_delete_uc = UserDeleteUseCase(user_repository)
        self.user_location_rol_list_uc = UserLocationRolListUseCase(
            user_location_rol_repository
        )
        self.user_location_rol_delete_uc = UserLocationRolDeleteUseCase(
            user_location_rol_repository
        )
        self.platform_delete_uc = PlatformDeleteUseCase(platform_repository)
        self.check_active_relations_uc = CheckActiveRelationsUseCase()
        self.check_last_admin_uc = CheckLastAdminUseCase()
        self.soft_delete_user_uc = SoftDeleteUserUseCase()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: DeleteUserInternalRequest,
    ) -> Union[str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        # 1. Validar que el usuario existe
        user = await self.user_read_uc.execute(
            config=config,
            params=UserRead(id=params.user_id)
        )
        if isinstance(user, str) or not user:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_NOT_FOUND.value,
                    params={"user_id": str(params.user_id)}
                ),
            )

        platform_id = user.platform_id

        # 2. Validar que no se esté eliminando a sí mismo
        if str(params.user_id) == str(config.token.user_id):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_CANNOT_DELETE_SELF.value
                ),
            )

        # 3. Verificar relaciones activas
        has_active_relations = await self.check_active_relations_uc.execute(
            config=config,
            user_id=params.user_id
        )
        if has_active_relations:
            return await self._handle_soft_delete(config=config, user=user)

        # 4. Obtener user_location_rols
        user_location_rols = await self.user_location_rol_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="user_id",
                        condition=CONDITION_TYPE.EQUALS,
                        value=str(params.user_id)
                    )
                ]
            )
        )

        # 5. Validar resultado de user_location_rols y ubicación del admin
        # Caso 1: Error al obtener roles (problema técnico)
        if isinstance(user_location_rols, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_ERROR_FETCHING_ROLES.value
                ),
            )
        
        # Caso 2: Usuario sin roles asignados (problema de integridad de datos)
        if not user_location_rols or len(user_location_rols) == 0:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_NO_ROLES_FOUND.value
                ),
            )
        
        # Caso 3: Verificar que el usuario pertenezca a la misma ubicación del admin
        admin_location_id = str(config.token.location_id)
        user_belongs_to_location = False
        
        for ulr in user_location_rols:
            if str(ulr.location_id) == admin_location_id:
                user_belongs_to_location = True
                break
        
        if not user_belongs_to_location:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_NOT_IN_LOCATION.value
                ),
            )

        # 6. Validar que no sea el único ADMIN de la ubicación
        is_last_admin = await self.check_last_admin_uc.execute(
            config=config,
            user_id=params.user_id,
            location_id=config.token.location_id,
            user_location_rols=user_location_rols
        )
        
        if is_last_admin:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_LAST_ADMIN.value
                ),
            )

        # 7. Intentar hard delete
        try:
            await self._execute_hard_delete(
                config=config,
                params=params,
                user_location_rols=user_location_rols,
                platform_id=platform_id
            )
            return None  # Hard delete exitoso
            
        except Exception:
            # Si falla el hard delete, hacer soft delete
            return await self._handle_soft_delete(config=config, user=user)

    async def _execute_hard_delete(
        self,
        config: Config,
        params: DeleteUserInternalRequest,
        user_location_rols,
        platform_id: UUID4
    ) -> None:
        """Ejecuta la eliminación física del usuario y sus registros relacionados."""
        
        # Eliminar user_location_rols
        if user_location_rols and not isinstance(user_location_rols, str):
            for ulr in user_location_rols:
                delete_result = await self.user_location_rol_delete_uc.execute(
                    config=config,
                    params=UserLocationRolDelete(id=ulr.id)
                )
                if isinstance(delete_result, str):
                    raise Exception("Error deleting user_location_rol")

        # Eliminar user
        user_deleted = await self.user_delete_uc.execute(
            config=config,
            params=UserDelete(id=params.user_id)
        )
        if isinstance(user_deleted, str):
            raise Exception("Error deleting user")

        # Eliminar platform
        platform_deleted = await self.platform_delete_uc.execute(
            config=config,
            params=PlatformDelete(id=platform_id)
        )
        if isinstance(platform_deleted, str):
            raise Exception("Error deleting platform")

    async def _handle_soft_delete(self, config: Config, user) -> str:
        """Maneja el soft delete y retorna el mensaje correspondiente."""
        soft_delete_result = await self.soft_delete_user_uc.execute(
            config=config,
            user=user
        )
        if isinstance(soft_delete_result, str):
            return soft_delete_result
        
        return await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_DELETE_USER_SOFT_DELETED.value
            ),
        )
