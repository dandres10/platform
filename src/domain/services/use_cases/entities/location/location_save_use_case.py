
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.location.index import Location, LocationSave
from src.domain.services.repositories.entities.i_location_repository import (
    ILocationRepository,
)
from src.infrastructure.database.mappers.location_mapper import (
    map_to_save_location_entity,
)


class LocationSaveUseCase:
    def __init__(self, location_repository: ILocationRepository):
        self.location_repository = location_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: LocationSave,
    ) -> Union[Location, str, None]:
        result = map_to_save_location_entity(params)
        result = await self.location_repository.save(config=config, params=result)
        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.dict() 

        return result
        