from typing import Any, List, Tuple, Union
from abc import ABC, abstractmethod
from src.core.models.config import Config
from src.domain.models.business.auth.create_api_token.create_api_token_request import (
    CreateApiTokenRequest,
)
from src.domain.models.business.auth.create_api_token.create_api_token_response import (
    CreateApiTokenResponse,
)
from src.domain.models.business.auth.login.auth_currencies_by_location import (
    AuthCurremciesByLocation,
)
from src.domain.models.business.auth.login.auth_locations import AuthLocations
from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.domain.models.business.auth.login.auth_login_response import CompanyLoginResponse
from src.domain.models.business.auth.login.auth_user_role_and_permissions import (
    AuthUserRoleAndPermissions,
)
from src.domain.models.business.auth.login.companies_by_user import CompaniesByUser
from src.domain.models.business.auth.login.menu import Menu
from src.domain.models.entities.company.company import Company


class IAuthRepository(ABC):
    @abstractmethod
    def initial_user_data(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[Tuple[Any], None]:
        pass

    @abstractmethod
    def user_role_and_permissions(
        self,
        config: Config,
        params: AuthUserRoleAndPermissions,
    ) -> Union[List[Tuple[Any]], None]:
        pass

    @abstractmethod
    def menu(
        self,
        config: Config,
        params: Menu,
    ) -> Union[List[Tuple[Any]], None]:
        pass

    @abstractmethod
    def currencies_by_location(
        self,
        config: Config,
        params: AuthCurremciesByLocation,
    ) -> Union[
        List[Tuple[Any]],
        None,
    ]:
        pass

    @abstractmethod
    def locations_by_user(
        self,
        config: Config,
        params: AuthLocations,
    ) -> Union[
        List[Tuple[Any]],
        None,
    ]:
        pass

    @abstractmethod
    def create_api_token(
        self,
        config: Config,
        params: CreateApiTokenRequest,
    ) -> Union[
        CreateApiTokenResponse,
        str,
    ]:
        pass

    @abstractmethod
    def companies_by_user(self, config: Config, params: CompaniesByUser) -> Union[
        List[CompanyLoginResponse],
        None,
    ]:
        pass
