from typing import Union, Tuple
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.entities.user_entity import UserEntity
from src.infrastructure.database.entities.language_entity import LanguageEntity
from src.infrastructure.database.entities.currency_entity import CurrencyEntity


class AuthInitialExternalUserDataUseCase:
    """
    Obtiene los datos iniciales de un usuario externo para el login.
    
    A diferencia del interno, no tiene location, country ni company.
    Solo obtiene: platform, user, language, currency.
    """
    
    def __init__(self):
        self.auth_repository = AuthRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        email: str,
    ) -> Union[
        Tuple[PlatformEntity, UserEntity, LanguageEntity, CurrencyEntity],
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT

        result = await self.auth_repository.initial_external_user_data(
            config=config, email=email
        )

        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND.value
                ),
            )

        return result
