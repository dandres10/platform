
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.geo_division_type.index import (
    GeoDivisionType,
    GeoDivisionTypeDelete,
    GeoDivisionTypeRead,
    GeoDivisionTypeSave,
    GeoDivisionTypeUpdate,
)



class IGeoDivisionTypeRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: GeoDivisionTypeSave,
    ) -> Union[GeoDivisionType, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: GeoDivisionTypeUpdate,
    ) -> Union[GeoDivisionType, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[GeoDivisionType], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: GeoDivisionTypeDelete,
    ) -> Union[GeoDivisionType, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: GeoDivisionTypeRead,
    ) -> Union[GeoDivisionType, None]:
        pass
