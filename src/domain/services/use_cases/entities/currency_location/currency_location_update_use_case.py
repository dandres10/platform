
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency_location.index import CurrencyLocation, CurrencyLocationUpdate
from src.domain.services.repositories.entities.i_currency_location_repository import (
    ICurrencyLocationRepository,
)
from src.core.config import settings
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity


class CurrencyLocationUpdateUseCase:
    def __init__(self, currency_location_repository: ICurrencyLocationRepository):
        self.currency_location_repository = currency_location_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: CurrencyLocationUpdate,
    ) -> Union[CurrencyLocation, str, None]:
        result = self.currency_location_repository.update(config=config, params=params)
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_UPDATE_FAILED.value),
            )

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.dict() 

        return result
        