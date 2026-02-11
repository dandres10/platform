
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.geography.index import (
    GeoDivisionTypeByCountryResponse,
    TypesByCountryRequest,
)
from src.infrastructure.database.repositories.business.geography_repository import (
    GeographyRepository,
)
from src.infrastructure.database.repositories.business.mappers.geography.geography_mapper import (
    map_to_geo_division_type_by_country_response,
)


class TypesByCountryUseCase:
    def __init__(self):
        self.geography_repository = GeographyRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self, config: Config, params: TypesByCountryRequest
    ) -> Union[List[GeoDivisionTypeByCountryResponse], str]:
        rows = await self.geography_repository.get_types_by_country(
            config=config, country_id=params.country_id
        )
        if not rows:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                ),
            )
        
        from src.infrastructure.database.entities.geo_division_type_entity import GeoDivisionTypeEntity
        
        result = []
        for row in rows:
            type_entity = GeoDivisionTypeEntity()
            type_entity.id = row.id
            type_entity.name = row.name
            type_entity.label = row.label
            
            result.append(
                map_to_geo_division_type_by_country_response(
                    type_entity=type_entity,
                    level=row.level,
                    count=row.count,
                )
            )
        return result
