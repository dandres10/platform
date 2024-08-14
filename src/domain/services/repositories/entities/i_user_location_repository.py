
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.user_location.index import (
    UserLocation,
    UserLocationDelete,
    UserLocationRead,
    UserLocationUpdate,
)

from src.infrastructure.database.entities.user_location_entity import UserLocationEntity


class IUserLocationRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: UserLocationEntity,
    ) -> Union[UserLocation, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: UserLocationUpdate,
    ) -> Union[UserLocation, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserLocation], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: UserLocationDelete,
    ) -> Union[UserLocation, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: UserLocationRead,
    ) -> Union[UserLocation, None]:
        pass
        