
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.platform.index import Platform, PlatformUpdate
from src.domain.services.repositories.entities.i_platform_repository import (
    IPlatformRepository,
)



class PlatformUpdateUseCase:
    def __init__(self, platform_repository: IPlatformRepository):
        self.platform_repository = platform_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: PlatformUpdate,
    ) -> Union[Platform, str, None]:
        result = await self.platform_repository.update(config=config, params=params)
        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_UPDATE_FAILED.value),
            )

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.dict() 

        return result
        