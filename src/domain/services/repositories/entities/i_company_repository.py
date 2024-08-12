
from typing import List, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.company.index import (
    Company,
    CompanyDelete,
    CompanyRead,
    CompanyUpdate,
)

from src.infrastructure.database.entities.company_entity import CompanyEntity


class ICompanyRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: CompanyEntity,
    ) -> Union[Company, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: CompanyUpdate,
    ) -> Union[Company, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Company], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: CompanyDelete,
    ) -> Union[Company, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: CompanyRead,
    ) -> Union[Company, None]:
        pass
        