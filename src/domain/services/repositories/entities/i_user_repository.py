
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.user.index import (
    User,
    UserDelete,
    UserRead,
    UserSave,
    UserUpdate,
)



class IUserRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: UserSave,
    ) -> Union[User, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: UserUpdate,
    ) -> Union[User, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[User], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: UserDelete,
    ) -> Union[User, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: UserRead,
    ) -> Union[User, None]:
        pass
        