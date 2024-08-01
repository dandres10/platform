from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.config import settings
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency.currency import Currency
from src.domain.models.entities.currency.currency_update import CurrencyUpdate
from src.domain.services.repositories.entities.i_currency_repository import (
    ICurrencyRepository,
)


class CurrencyUpdateUseCase:
    def __init__(self, currency_repository: ICurrencyRepository):
        self.currency_repository = currency_repository

    def execute(
        self,
        config: Config,
        params: CurrencyUpdate,
    ) -> Union[Currency, str, None]:
        result = self.currency_repository.update(config=config, params=params)
        result = result.dict()
        if not result:
            return "No se pudo realizar la actualización, no se encontro registro para actualizar"
        return result


if settings.has_track:
    CurrencyUpdateUseCase.execute = execute_transaction(LAYER.D_S_U_E.value)(
        CurrencyUpdateUseCase.execute
    )
