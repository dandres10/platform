
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.user_location_rol.index import (
    UserLocationRol,
    UserLocationRolDelete,
    UserLocationRolRead,
    UserLocationRolUpdate,
)

from src.infrastructure.database.entities.user_location_rol_entity import UserLocationRolEntity


class IUserLocationRolRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: UserLocationRolEntity,
    ) -> Union[UserLocationRol, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: UserLocationRolUpdate,
    ) -> Union[UserLocationRol, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserLocationRol], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: UserLocationRolDelete,
    ) -> Union[UserLocationRol, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: UserLocationRolRead,
    ) -> Union[UserLocationRol, None]:
        pass
        