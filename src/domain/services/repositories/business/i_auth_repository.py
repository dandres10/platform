from typing import Any, List, Tuple, Union
from abc import ABC, abstractmethod
from src.core.models.config import Config
from src.domain.models.business.auth.auth_login_request import AuthLoginRequest
from src.domain.models.entities.permission.permission import Permission
from src.domain.models.entities.rol.rol import Rol
from src.domain.models.entities.user.user import User

class IAuthRepository(ABC):
    @abstractmethod
    def login(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[List[Tuple[Any]], None]:
        pass