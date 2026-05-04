
from typing import List, Optional, Union
from abc import ABC, abstractmethod

from src.core.models.config import Config
from src.core.models.filter import Pagination

from src.domain.models.entities.company_currency.index import (
    CompanyCurrency,
    CompanyCurrencyDelete,
    CompanyCurrencyRead,
    CompanyCurrencySave,
    CompanyCurrencyUpdate,
)



class ICompanyCurrencyRepository(ABC):
    @abstractmethod
    def save(
        self,
        config: Config,
        params: CompanyCurrencySave,
    ) -> Union[CompanyCurrency, None]:
        pass

    @abstractmethod
    def update(
        self,
        config: Config,
        params: CompanyCurrencyUpdate,
    ) -> Union[CompanyCurrency, None]:
        pass

    @abstractmethod
    def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[CompanyCurrency], None]:
        pass

    @abstractmethod
    def delete(
        self,
        config: Config,
        params: CompanyCurrencyDelete,
    ) -> Union[CompanyCurrency, None]:
        pass

    @abstractmethod
    def read(
        self,
        config: Config,
        params: CompanyCurrencyRead,
    ) -> Union[CompanyCurrency, None]:
        pass

    @abstractmethod
    def find_base_by_company(
        self,
        config: Config,
        company_id,
    ) -> Optional[CompanyCurrency]:
        pass
