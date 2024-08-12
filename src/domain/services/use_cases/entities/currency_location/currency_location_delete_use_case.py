
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency_location.index import CurrencyLocationDelete, CurrencyLocation
from src.domain.services.repositories.entities.i_currency_location_repository import (
    ICurrencyLocationRepository,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class CurrencyLocationDeleteUseCase:
    def __init__(self, currency_location_repository: ICurrencyLocationRepository):
        self.currency_location_repository = currency_location_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)    
    def execute(
        self,
        config: Config,
        params: CurrencyLocationDelete,
    ) -> Union[CurrencyLocation, str, None]:
        result = self.currency_location_repository.delete(config=config, params=params)
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )
        result = result.dict()
        return result
        