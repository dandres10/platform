from typing import Union, Tuple
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency.currency import Currency
from src.domain.models.entities.language.language import Language
from src.domain.models.entities.platform.platform import Platform
from src.domain.models.entities.user.user import User
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)


class AuthInitialExternalUserDataUseCase:
    def __init__(self):
        self.auth_repository = AuthRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        email: str,
    ) -> Union[Tuple[Platform, User, Language, Currency], str]:
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
