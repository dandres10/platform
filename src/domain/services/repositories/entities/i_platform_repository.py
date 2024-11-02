
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.platform.index import (
    Platform,
    PlatformDelete,
    PlatformRead,
    PlatformUpdate,
)

from src.infrastructure.database.entities.platform_entity import PlatformEntity


class IPlatformRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: PlatformEntity,
    ) -> Union[Platform, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: PlatformUpdate,
    ) -> Union[Platform, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Platform], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: PlatformDelete,
    ) -> Union[Platform, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: PlatformRead,
    ) -> Union[Platform, None]:
        pass
        