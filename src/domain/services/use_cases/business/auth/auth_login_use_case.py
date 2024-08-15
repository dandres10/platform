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
from src.domain.models.business.auth.index import AuthLoginRequest, AuthLoginResponse
from src.domain.models.entities.user.user import User
from src.infrastructure.database.repositories.auth_repository import AuthRepository
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
        self.auth_Repository = AuthRepository()
        self.message = Message()
        self.password = Password()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[AuthLoginResponse, str, None]:
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

        respueseta = self.auth_Repository.login(config=config, params=params)

        (
            user_entity,
            rol_entity,
            platform_entity,
            language_entity,
            currency_location_entity,
            currency_entity,
        ) = respueseta



        result = AuthLoginResponse(
            user_id=user.id,
            rol_id=user.rol_id,
            rol_name=rol_entity.name,
            rol_code=rol_entity.code,
            platform_id=user.platform_id,
            language_id=platform_entity.language_id,
            location_id=platform_entity.location_id,
            currency_id=currency_entity.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone,
            state=user.state,

        )

        return result
