
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency.index import Currency, CurrencySave
from src.domain.services.repositories.entities.i_currency_repository import (
    ICurrencyRepository,
)
from src.core.config import settings
from src.infrastructure.database.mappers.currency_mapper import (
    map_to_save_currency_entity,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class CurrencySaveUseCase:
    def __init__(self, currency_repository: ICurrencyRepository):
        self.currency_repository = currency_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: CurrencySave,
    ) -> Union[Currency, str, None]:
        result = map_to_save_currency_entity(params)
        result = self.currency_repository.save(config=config, params=result)
        if not result:
            return self.message.get_message(
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
        