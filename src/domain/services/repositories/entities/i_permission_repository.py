
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.permission.index import (
    Permission,
    PermissionDelete,
    PermissionRead,
    PermissionUpdate,
)

from src.infrastructure.database.entities.permission_entity import PermissionEntity


class IPermissionRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: PermissionEntity,
    ) -> Union[Permission, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: PermissionUpdate,
    ) -> Union[Permission, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Permission], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: PermissionDelete,
    ) -> Union[Permission, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: PermissionRead,
    ) -> Union[Permission, None]:
        pass
        