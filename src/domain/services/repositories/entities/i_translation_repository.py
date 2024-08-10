
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.translation.index import (
    Translation,
    TranslationDelete,
    TranslationRead,
    TranslationUpdate,
)

from src.infrastructure.database.entities.translation_entity import TranslationEntity


class ITranslationRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: TranslationEntity,
    ) -> Union[Translation, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: TranslationUpdate,
    ) -> Union[Translation, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Translation], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: TranslationDelete,
    ) -> Union[Translation, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: TranslationRead,
    ) -> Union[Translation, None]:
        pass
        