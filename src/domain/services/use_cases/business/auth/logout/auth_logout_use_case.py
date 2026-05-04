from typing import List, Union
from src.core.classes.async_message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.logout.auth_logout_response import AuthLogoutResponse
from src.domain.models.entities.user.user_read import UserRead
from src.domain.models.entities.user.user_update import UserUpdate
from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase,
)
from src.domain.services.use_cases.entities.user.user_update_use_case import (
    UserUpdateUseCase,
)
from src.core.config import settings
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

        # SPEC-019: response composition (UserRead DTO -> UserUpdate)
        user_update_params = UserUpdate(
            id=user_read.id,
            platform_id=user_read.platform_id,
            password=user_read.password,
            email=user_read.email,
            identification=user_read.identification,
            first_name=user_read.first_name,
            last_name=user_read.last_name,
            phone=user_read.phone,
            refresh_token=user_read.refresh_token,
            state=user_read.state,
        )

        user_update = await self.user_update_use_case.execute(
            config=config, params=user_update_params
        )

        if isinstance(user_update, str):
            return user_update

        translated_message = await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_LOGOUT_SUCCESS.value
            ),
        )

        result = AuthLogoutResponse(message=translated_message)

        return result
