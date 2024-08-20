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
from src.domain.models.business.auth.auth_login_response import (
    BasePlatformConfiguration,
    PermissionLoginResponse,
)
from src.domain.models.business.auth.index import AuthLoginRequest, AuthLoginResponse
from src.domain.models.business.auth.security import Security
from src.infrastructure.database.entities.permission_entity import PermissionEntity
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.infrastructure.database.repositories.business.mappers.auth_mapper import (
    map_to_company_login_response,
    map_to_country_login_response,
    map_to_currecy_login_response,
    map_to_language_login_response,
    map_to_location_login_response,
    map_to_permission_response,
    map_to_platform_login_response,
    map_to_rol_login_response,
    map_to_user_login_response,
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)
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
        permissions: List[PermissionLoginResponse] = []
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

        initial_user_data = self.auth_Repository.initial_user_data(
            config=config, params=params
        )

        if not initial_user_data:
            print("no se encontro informacion relacionada")
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        (
            platform_entity,
            user_entity,
            language_entity,
            location_entity,
            currency_entity,
            country_entity,
            company_entity,
        ) = initial_user_data

        user_role_and_permissions = self.auth_Repository.user_role_and_permissions(
            config=config,
            params=Security(email=params.email, location=location_entity.id),
        )

        if not user_role_and_permissions:
            print("no se encontro informacion relacionada #2")
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        

        for user_role_and_permission in user_role_and_permissions:
            user_location_rol_q, user_q, rol_q, rol_permission_q, permission_q = (
                user_role_and_permission
            )
            permissions.append(map_to_permission_response(permission_entity=permission_q))

        result = AuthLoginResponse(
            base_platform_configuration=BasePlatformConfiguration(
                user=map_to_user_login_response(user_entity=user_entity),
                currecy=map_to_currecy_login_response(currency_entity=currency_entity),
                location=map_to_location_login_response(
                    location_entity=location_entity
                ),
                language=map_to_language_login_response(
                    language_entity=language_entity
                ),
                platform=map_to_platform_login_response(
                    platform_entity=platform_entity
                ),
                country=map_to_country_login_response(country_entity=country_entity),
                company=map_to_company_login_response(company_entity=company_entity),
                rol=map_to_rol_login_response(rol_entity=rol_q),
                permissions=permissions
            )
        )

        return result
