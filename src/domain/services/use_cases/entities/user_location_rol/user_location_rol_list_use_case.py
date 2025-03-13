
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.domain.models.entities.user_location_rol.index import UserLocationRol
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.services.repositories.entities.i_user_location_rol_repository import (
    IUserLocationRolRepository,
)


class UserLocationRolListUseCase:
    def __init__(self, user_location_rol_repository: IUserLocationRolRepository):
        self.user_location_rol_repository = user_location_rol_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserLocationRol], str, None]:
        results = await self.user_location_rol_repository.list(config=config, params=params)
        if not results:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                ),
            )
        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return results
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return [result.dict() for result in results]

        return results
        