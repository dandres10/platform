
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.geography.index import (
    GeoDivisionItemResponse,
    ChildrenRequest,
)
from src.infrastructure.database.repositories.business.geography_repository import (
    GeographyRepository,
)
from src.infrastructure.database.repositories.business.mappers.geography.geography_mapper import (
    map_to_list_geo_division_item_response,
)


class ChildrenUseCase:
    def __init__(self):
        self.geography_repository = GeographyRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self, config: Config, params: ChildrenRequest
    ) -> Union[List[GeoDivisionItemResponse], str]:
        rows = await self.geography_repository.get_children(
            config=config, parent_id=params.parent_id
        )
        if not rows:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                ),
            )
        return map_to_list_geo_division_item_response(rows)
