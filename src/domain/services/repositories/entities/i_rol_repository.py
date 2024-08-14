
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.rol.index import (
    Rol,
    RolDelete,
    RolRead,
    RolUpdate,
)

from src.infrastructure.database.entities.rol_entity import RolEntity


class IRolRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: RolEntity,
    ) -> Union[Rol, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: RolUpdate,
    ) -> Union[Rol, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Rol], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: RolDelete,
    ) -> Union[Rol, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: RolRead,
    ) -> Union[Rol, None]:
        pass
        