
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.api_token.index import (
    ApiToken,
    ApiTokenDelete,
    ApiTokenRead,
    ApiTokenUpdate,
)

from src.infrastructure.database.entities.api_token_entity import ApiTokenEntity


class IApiTokenRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: ApiTokenEntity,
    ) -> Union[ApiToken, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: ApiTokenUpdate,
    ) -> Union[ApiToken, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[ApiToken], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: ApiTokenDelete,
    ) -> Union[ApiToken, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: ApiTokenRead,
    ) -> Union[ApiToken, None]:
        pass
        