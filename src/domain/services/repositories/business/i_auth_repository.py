from typing import Any, List, Tuple, Union
from abc import ABC, abstractmethod
from src.core.models.config import Config
from src.domain.models.business.auth.auth_login_request import AuthLoginRequest
from src.domain.models.business.auth.auth_user_role_and_permissions import AuthUserRoleAndPermissions
from src.domain.models.business.auth.menu import Menu




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
