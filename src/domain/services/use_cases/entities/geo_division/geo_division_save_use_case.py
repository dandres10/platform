
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.geo_division.index import GeoDivision, GeoDivisionSave
from src.domain.services.repositories.entities.i_geo_division_repository import (
    IGeoDivisionRepository,
)
from src.infrastructure.database.mappers.geo_division_mapper import (
    map_to_save_geo_division_entity,
)


class GeoDivisionSaveUseCase:
    def __init__(self, geo_division_repository: IGeoDivisionRepository):
        self.geo_division_repository = geo_division_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: GeoDivisionSave,
    ) -> Union[GeoDivision, str, None]:
        result = map_to_save_geo_division_entity(params)
        result = await self.geo_division_repository.save(config=config, params=result)
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
