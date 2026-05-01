
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.rol_permission.index import (
    RolPermission,
    RolPermissionDelete,
    RolPermissionRead,
    RolPermissionSave,
    RolPermissionUpdate,
)



class IRolPermissionRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: RolPermissionSave,
    ) -> Union[RolPermission, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: RolPermissionUpdate,
    ) -> Union[RolPermission, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[RolPermission], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: RolPermissionDelete,
    ) -> Union[RolPermission, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: RolPermissionRead,
    ) -> Union[RolPermission, None]:
        pass
        