
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.geo_division.index import (
    GeoDivision,
    GeoDivisionDelete,
    GeoDivisionRead,
    GeoDivisionUpdate,
)

from src.infrastructure.database.entities.geo_division_entity import GeoDivisionEntity


class IGeoDivisionRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: GeoDivisionEntity,
    ) -> Union[GeoDivision, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: GeoDivisionUpdate,
    ) -> Union[GeoDivision, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[GeoDivision], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: GeoDivisionDelete,
    ) -> Union[GeoDivision, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: GeoDivisionRead,
    ) -> Union[GeoDivision, None]:
        pass
