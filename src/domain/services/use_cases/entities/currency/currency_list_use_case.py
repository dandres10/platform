
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.enums.response_type import RESPONSE_TYPE
from src.domain.models.entities.currency.index import Currency
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.services.repositories.entities.i_currency_repository import (
    ICurrencyRepository,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class CurrencyListUseCase:
    def __init__(self, currency_repository: ICurrencyRepository):
        self.currency_repository = currency_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Currency], str, None]:
        results = self.currency_repository.list(config=config, params=params)
        if not results:
            return self.message.get_message(
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
        