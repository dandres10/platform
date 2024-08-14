from typing import List, Union
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.filter import FilterManager, Pagination
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.index import AuthLoginRequest, AuthLoginResponse
from src.domain.models.entities.user.user import User
from src.infrastructure.database.repositories.user_repository import UserRepository
from src.domain.services.use_cases.entities.user.index import (
    UserListUseCase,
)
from src.core.config import settings

user_repository = UserRepository()


class AuthLoginUseCase:
    def __init__(
        self,
    ):
        self.user_list_use_case = UserListUseCase(user_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[AuthLoginResponse, str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT
        filters_user: List[FilterManager] = [
            FilterManager(field="email", condition="==", value=params.email)
        ]

        pagination_user: Pagination = Pagination(
            all_data=True, filters=filters_user
        )

        [user] = self.user_list_use_case.execute(config=config, params=pagination_user)

        if not user:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND.value
                ),
            )

        result = AuthLoginResponse(
            user_id=user.id,
            rol_id=user.rol_id,
            platform_id=user.platform_id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            state=user.state,
        )

        return result
