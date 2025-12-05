from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.entities.user.index import UserUpdate
from src.domain.services.use_cases.entities.user.user_update_use_case import (
    UserUpdateUseCase
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)


user_repository = UserRepository()


class SoftDeleteUserExternalUseCase:
    """
    Inactiva un usuario externo (soft delete) actualizando state=False.
    Se usa cuando el usuario tiene relaciones activas y no puede ser eliminado físicamente.
    El usuario será eliminado permanentemente después de 1 mes.
    """
    
    def __init__(self):
        self.user_update_uc = UserUpdateUseCase(user_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        user
    ) -> Union[str, bool]:
        """
        Inactiva el usuario externo actualizando state=False.
        
        Args:
            config: Configuración de la petición
            user: Objeto usuario a inactivar
            
        Returns:
            Union[str, bool]: True si éxito, str con mensaje de error si falla
        """
        update_params = UserUpdate(
            id=user.id,
            platform_id=user.platform_id,
            password=user.password,
            email=user.email,
            identification=user.identification,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            refresh_token=user.refresh_token,
            state=False  # Inactivar usuario
        )
        
        result = await self.user_update_uc.execute(
            config=config,
            params=update_params
        )
        
        if isinstance(result, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_ERROR_SOFT_DELETE.value
                ),
            )
        
        return True

