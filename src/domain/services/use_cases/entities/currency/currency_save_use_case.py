from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.config import settings
from src.domain.models.entities.currency.currency import Currency
from src.domain.models.entities.currency.currency_save import CurrencySave
from src.domain.services.repositories.entities.i_currency_repository import (
    ICurrencyRepository,
)
from src.infrastructure.database.mappers.currency_mapper import (
    map_to_save_currency_entity,
)


class CurrencySaveUseCase:
    def __init__(self, currency_repository: ICurrencyRepository):
        self.currency_repository = currency_repository

    def execute(
        self,
        config: Config,
        params: CurrencySave,
    ) -> Union[Currency, str, None]:
        currency = map_to_save_currency_entity(params)
        result = self.currency_repository.save(config=config, params=currency)
        result = result.dict()
        if not result:
            return "Error en el flujo, contactar al administrador"
        return result


if settings.has_track:
    CurrencySaveUseCase.execute = execute_transaction(LAYER.D_S_U_E.value)(
        CurrencySaveUseCase.execute
    )
