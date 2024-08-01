from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency.currency import Currency
from src.domain.models.entities.currency.currency_read import CurrencyRead
from src.domain.services.repositories.entities.i_currency_repository import (
    ICurrencyRepository,
)


class CurrencyReadUseCase:
    def __init__(self, currency_repository: ICurrencyRepository):
        self.currency_repository = currency_repository

    def execute(
        self,
        config: Config,
        params: CurrencyRead,
    ) -> Union[Currency, str, None]:
        result = self.currency_repository.read(config=config, params=params)
        result = result.dict()
        if not result:
            return "No se encontro el registro"
        return result


if settings.has_track:
    CurrencyReadUseCase.execute = execute_transaction(LAYER.D_S_U_E.value)(
        CurrencyReadUseCase.execute
    )
