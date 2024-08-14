
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.menu.index import (
    Menu,
    MenuDelete,
    MenuRead,
    MenuUpdate,
)

from src.infrastructure.database.entities.menu_entity import MenuEntity


class IMenuRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: MenuEntity,
    ) -> Union[Menu, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: MenuUpdate,
    ) -> Union[Menu, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Menu], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: MenuDelete,
    ) -> Union[Menu, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: MenuRead,
    ) -> Union[Menu, None]:
        pass
        