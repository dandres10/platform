from typing import List, Union
from src.core.classes.async_message import Message
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.logout.auth_logout_response import AuthLogoutResponse
from src.domain.models.entities.user.user_read import UserRead
from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase,
)
from src.domain.services.use_cases.entities.user.user_update_use_case import (
    UserUpdateUseCase,
)
from src.core.config import settings
from src.infrastructure.database.repositories.business.mappers.auth.login.login_mapper import (
    map_to_user_read,
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)


user_repository = UserRepository()


class AuthLogoutUseCase:
    def __init__(
        self,
    ):
        self.user_update_use_case = UserUpdateUseCase(user_repository=user_repository)
        self.user_read_use_case = UserReadUseCase(user_repository=user_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(self, config: Config) -> Union[AuthLogoutResponse, str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        user_read = await self.user_read_use_case.execute(
            config=config, params=UserRead(id=config.token.user_id)
        )

        if isinstance(user_read, str):
            return user_read

        user_read.refresh_token = ""

        user_update = await self.user_update_use_case.execute(
            config=config, params=map_to_user_read(user_read=user_read)
        )

        if isinstance(user_update, str):
            return user_update

        result = AuthLogoutResponse(message="cierra de session con exito.")

        return result
