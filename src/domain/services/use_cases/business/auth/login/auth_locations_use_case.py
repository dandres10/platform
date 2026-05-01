from typing import List, Union
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_locations import AuthLocations
from src.domain.models.business.auth.login.auth_login_response import (
    LocationLoginResponse,
)
from src.core.config import settings
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.core.classes.async_message import Message


class AuthLocationsUseCase:
    def __init__(
        self,
    ):
        self.auth_repository = AuthRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(self, config: Config, params: AuthLocations) -> Union[
        List[LocationLoginResponse],
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT

        result = await self.auth_repository.locations_by_user(
            config=config, params=params
        )

        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        return result
