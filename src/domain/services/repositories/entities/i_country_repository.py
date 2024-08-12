
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.country.index import (
    Country,
    CountryDelete,
    CountryRead,
    CountryUpdate,
)

from src.infrastructure.database.entities.country_entity import CountryEntity


class ICountryRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: CountryEntity,
    ) -> Union[Country, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: CountryUpdate,
    ) -> Union[Country, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Country], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: CountryDelete,
    ) -> Union[Country, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: CountryRead,
    ) -> Union[Country, None]:
        pass
        