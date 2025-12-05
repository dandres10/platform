from typing import Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.business.auth.delete_user_external import (
    DeleteUserExternalRequest
)
from src.domain.models.entities.user.index import UserRead, UserDelete
from src.domain.models.entities.platform.index import PlatformDelete

from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase
)
from src.domain.services.use_cases.entities.user.user_delete_use_case import (
    UserDeleteUseCase
)
from src.domain.services.use_cases.entities.platform.platform_delete_use_case import (
    PlatformDeleteUseCase
)

from .check_active_relations_use_case import CheckActiveRelationsExternalUseCase
from .soft_delete_user_use_case import SoftDeleteUserExternalUseCase

from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)
from src.infrastructure.database.repositories.entities.platform_repository import (
    PlatformRepository
)


user_repository = UserRepository()
platform_repository = PlatformRepository()


class DeleteUserExternalUseCase:
    def __init__(self):
        self.user_read_uc = UserReadUseCase(user_repository)
        self.user_delete_uc = UserDeleteUseCase(user_repository)
        self.platform_delete_uc = PlatformDeleteUseCase(platform_repository)
        self.check_active_relations_uc = CheckActiveRelationsExternalUseCase()
        self.soft_delete_user_uc = SoftDeleteUserExternalUseCase()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: DeleteUserExternalRequest,
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
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_NOT_FOUND.value,
                    params={"user_id": str(params.user_id)}
                ),
            )

        platform_id = user.platform_id

        # 2. Solo puede eliminar su propia cuenta (self-delete)
        if str(params.user_id) != str(config.token.user_id):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_UNAUTHORIZED.value
                ),
            )

        # 3. Verificar relaciones activas
        has_active_relations = await self.check_active_relations_uc.execute(
            config=config,
            user_id=params.user_id
        )
        if has_active_relations:
            return await self._handle_soft_delete(config=config, user=user)

        # 4. Intentar hard delete
        try:
            await self._execute_hard_delete(
                config=config,
                params=params,
                platform_id=platform_id
            )
            return None  # Hard delete exitoso
            
        except Exception:
            # Si falla el hard delete, hacer soft delete
            return await self._handle_soft_delete(config=config, user=user)

    async def _execute_hard_delete(
        self,
        config: Config,
        params: DeleteUserExternalRequest,
        platform_id: UUID4
    ) -> None:
        """Ejecuta la eliminación física del usuario y sus registros relacionados."""
        
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
                key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_SOFT_DELETED.value
            ),
        )
