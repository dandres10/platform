from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency.currency import Currency
from src.domain.services.repositories.entities.i_currency_repository import (
    ICurrencyRepository,
)


class CurrencyListUseCase:
    def __init__(self, currency_repository: ICurrencyRepository):
        self.currency_repository = currency_repository

    def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Currency], str, None]:
        results = self.currency_repository.list(config=config, params=params)
        results = [result.dict() for result in results]
        if not results:
            return "No se encontraron resultados"
        return results


if settings.has_track:
    CurrencyListUseCase.execute = execute_transaction(LAYER.D_S_U_E.value)(
        CurrencyListUseCase.execute
    )
