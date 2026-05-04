from typing import Union
from src.core.classes.async_message import Message
from src.core.classes.password import Password
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.filter import FilterManager, Pagination
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.domain.models.entities.user.user import User
from src.domain.services.use_cases.entities.user.user_list_use_case import (
    UserListUseCase,
)
from src.core.config import settings
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)


user_repository = UserRepository()


class AuthValidateUserUseCase:
    def __init__(
        self,
    ):
        self.user_list_use_case = UserListUseCase(user_repository)
        self.password = Password()
        self.message = Message()

    # SPEC-030 T3
    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[User, str]:
        config.response_type = RESPONSE_TYPE.OBJECT

        result_users_list = await self.user_list_use_case.execute(
            config=config,
            params=Pagination(
                all_data=True,
                filters=[
                    FilterManager(
                        field="email",
                        condition=CONDITION_TYPE.EQUALS.value,
                        value=params.email,
                    )
                ],
            ),
        )

        # SPEC-030 T1
        if (
            not result_users_list
            or isinstance(result_users_list, str)
            or not isinstance(result_users_list, list)
            or len(result_users_list) != 1
        ):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_LOGIN_INVALID_CREDENTIALS.value
                ),
            )

        user = result_users_list[0]

        check_password = self.password.check_password(
            password=params.password, hashed_password=user.password
        )

        if not check_password:
            # SPEC-030 T1
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_LOGIN_INVALID_CREDENTIALS.value
                ),
            )

        # SPEC-030 T3
        return user
