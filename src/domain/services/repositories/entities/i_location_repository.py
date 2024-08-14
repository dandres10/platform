
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.location.index import (
    Location,
    LocationDelete,
    LocationRead,
    LocationUpdate,
)

from src.infrastructure.database.entities.location_entity import LocationEntity


class ILocationRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: LocationEntity,
    ) -> Union[Location, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: LocationUpdate,
    ) -> Union[Location, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Location], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: LocationDelete,
    ) -> Union[Location, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: LocationRead,
    ) -> Union[Location, None]:
        pass
        