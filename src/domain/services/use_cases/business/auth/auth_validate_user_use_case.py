from typing import List, Union
from src.core.classes.message import Message
from src.core.classes.password import Password
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.filter import FilterManager, Pagination
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.auth_login_request import AuthLoginRequest
from src.domain.services.use_cases.entities.user.user_list_use_case import UserListUseCase
from src.core.config import settings
from src.infrastructure.database.repositories.entities.user_repository import UserRepository


user_repository = UserRepository()

class AuthValidateUserUseCase:
    def __init__(
        self,
    ):
        self.user_list_use_case = UserListUseCase(user_repository)
        self.password = Password()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[
        bool,
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT

        filters_user: List[FilterManager] = [
            FilterManager(
                field="email", condition=CONDITION_TYPE.EQUALS.value, value=params.email
            )
        ]

        result_users_list = self.user_list_use_case.execute(
            config=config, params=Pagination(all_data=True, filters=filters_user)
        )

        if isinstance(result_users_list, str):
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        [user] = result_users_list

        check_password = self.password.check_password(
            password=params.password, hashed_password=user.password
        )

        if not check_password:
            print("contraseña es incorrecta")
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        

        return True
