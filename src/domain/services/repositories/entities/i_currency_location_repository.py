
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.currency_location.index import (
    CurrencyLocation,
    CurrencyLocationDelete,
    CurrencyLocationRead,
    CurrencyLocationUpdate,
)

from src.infrastructure.database.entities.currency_location_entity import CurrencyLocationEntity


class ICurrencyLocationRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: CurrencyLocationEntity,
    ) -> Union[CurrencyLocation, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: CurrencyLocationUpdate,
    ) -> Union[CurrencyLocation, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[CurrencyLocation], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: CurrencyLocationDelete,
    ) -> Union[CurrencyLocation, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: CurrencyLocationRead,
    ) -> Union[CurrencyLocation, None]:
        pass
        