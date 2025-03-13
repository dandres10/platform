from typing import Tuple, Union
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_initial_user_data import AuthInitialUserData
from src.infrastructure.database.entities.company_entity import CompanyEntity
from src.infrastructure.database.entities.country_entity import CountryEntity
from src.infrastructure.database.entities.currency_entity import CurrencyEntity
from src.infrastructure.database.entities.language_entity import LanguageEntity
from src.infrastructure.database.entities.location_entity import LocationEntity
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.entities.user_entity import UserEntity
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.core.config import settings
from src.core.classes.async_message import Message


class AuthInitialUserDataUseCase:
    def __init__(
        self,
    ):
        self.auth_repository = AuthRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: AuthInitialUserData,
    ) -> Union[
        Tuple[
            PlatformEntity,
            UserEntity,
            LanguageEntity,
            LocationEntity,
            CurrencyEntity,
            CountryEntity,
            CompanyEntity,
        ],
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT

        result = await self.auth_repository.initial_user_data(config=config, params=params)

        if not result:
            print("no se encontro informacion relacionada")
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        return result
