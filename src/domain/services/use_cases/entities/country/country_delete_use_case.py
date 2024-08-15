
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.country.index import CountryDelete, Country
from src.domain.services.repositories.entities.i_country_repository import (
    ICountryRepository,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class CountryDeleteUseCase:
    def __init__(self, country_repository: ICountryRepository):
        self.country_repository = country_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)    
    def execute(
        self,
        config: Config,
        params: CountryDelete,
    ) -> Union[Country, str, None]:
        result = self.country_repository.delete(config=config, params=params)
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.dict()

        return result
        