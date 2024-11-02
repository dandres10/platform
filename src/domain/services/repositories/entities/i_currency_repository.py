
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.currency.index import (
    Currency,
    CurrencyDelete,
    CurrencyRead,
    CurrencyUpdate,
)

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
        