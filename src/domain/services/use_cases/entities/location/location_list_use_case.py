
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.domain.models.entities.location.index import Location
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.services.repositories.entities.i_location_repository import (
    ILocationRepository,
)


class LocationListUseCase:
    def __init__(self, location_repository: ILocationRepository):
        self.location_repository = location_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Location], str, None]:
        results = await self.location_repository.list(config=config, params=params)
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
        