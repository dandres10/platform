from typing import List, Union
from abc import ABC, abstractmethod

from pydantic import UUID4
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.domain.models.entities.currency.currency import Currency
from src.domain.models.entities.currency.currency_delete import CurrencyDelete
from src.domain.models.entities.currency.currency_read import CurrencyRead
from src.domain.models.entities.currency.currency_update import CurrencyUpdate
from src.infrastructure.database.entities.currency_entity import CurrencyEntity


class ICurrencyRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: CurrencyEntity,
    ) -> Union[Currency, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: CurrencyUpdate,
    ) -> Union[Currency, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Currency], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: CurrencyDelete,
    ) -> Union[Currency, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: CurrencyRead,
    ) -> Union[Currency, None]:
        pass
