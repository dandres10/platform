
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user_country.index import UserCountry
from src.domain.services.repositories.entities.i_user_country_repository import (
    IUserCountryRepository,
)


class UserCountryListUseCase:
    def __init__(self, user_country_repository: IUserCountryRepository):
        self.user_country_repository = user_country_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserCountry], str, None]:
        result = await self.user_country_repository.list(config=config, params=params)
        if not result:
            return None

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return [item.model_dump() for item in result]

        return result
