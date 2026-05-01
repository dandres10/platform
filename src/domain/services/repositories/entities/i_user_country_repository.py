
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.user_country.index import (
    UserCountry,
    UserCountryDelete,
    UserCountryRead,
    UserCountrySave,
    UserCountryUpdate,
)



class IUserCountryRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: UserCountrySave,
    ) -> Union[UserCountry, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: UserCountryUpdate,
    ) -> Union[UserCountry, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserCountry], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: UserCountryDelete,
    ) -> Union[UserCountry, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: UserCountryRead,
    ) -> Union[UserCountry, None]:
        pass
