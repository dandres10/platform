
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.menu_permission.index import (
    MenuPermission,
    MenuPermissionDelete,
    MenuPermissionRead,
    MenuPermissionUpdate,
)

from src.infrastructure.database.entities.menu_permission_entity import MenuPermissionEntity


class IMenuPermissionRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: MenuPermissionEntity,
    ) -> Union[MenuPermission, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: MenuPermissionUpdate,
    ) -> Union[MenuPermission, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[MenuPermission], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: MenuPermissionDelete,
    ) -> Union[MenuPermission, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: MenuPermissionRead,
    ) -> Union[MenuPermission, None]:
        pass
        