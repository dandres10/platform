from typing import List, Union
from src.core.classes.message import Message
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.auth_initial_user_data import AuthInitialUserData
from src.domain.models.business.auth.auth_login_response import (
    BasePlatformConfiguration,
)
from src.domain.models.business.auth.auth_user_role_and_permissions import (
    AuthUserRoleAndPermissions,
)
from src.domain.models.business.auth.index import (
    AuthLoginRequest,
    AuthLoginResponse,
    AuthMenu,
)
from src.domain.services.use_cases.business.auth.auth_initial_user_data_use_case import (
    AuthInitialUserDataUseCase,
)
from src.domain.services.use_cases.business.auth.auth_menu_use_case import (
    AuthMenuUseCase,
)
from src.domain.services.use_cases.business.auth.auth_user_role_and_permissions import (
    AuthUserRoleAndPermissionsUseCase,
)
from src.domain.services.use_cases.business.auth.auth_validate_user_use_case import (
    AuthValidateUserUseCase,
)
from src.infrastructure.database.repositories.business.mappers.auth_mapper import (
    map_to_company_login_response,
    map_to_country_login_response,
    map_to_currecy_login_response,
    map_to_language_login_response,
    map_to_location_login_response,
    map_to_platform_login_response,
    map_to_rol_login_response,
    map_to_user_login_response,
)
from src.core.config import settings

class AuthLoginUseCase:
    def __init__(
        self,
    ):
        self.auth_validate_user_use_case = AuthValidateUserUseCase()
        self.auth_initial_user_data_use_case = AuthInitialUserDataUseCase()
        self.auth_menu_use_case = AuthMenuUseCase()
        self.auth_user_role_and_permissions_use_case = (
            AuthUserRoleAndPermissionsUseCase()
        )
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[AuthLoginResponse, str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        user_validator = self.auth_validate_user_use_case.execute(
            config=config, params=params
        )
        if isinstance(user_validator, str):
            return user_validator

        initial_user_data = self.auth_initial_user_data_use_case.execute(
            config=config, params=AuthInitialUserData(email=params.email)
        )
        if isinstance(initial_user_data, str):
            return initial_user_data

        (
            platform_entity,
            user_entity,
            language_entity,
            location_entity,
            currency_entity,
            country_entity,
            company_entity,
        ) = initial_user_data

        user_role_and_permissions = (
            self.auth_user_role_and_permissions_use_case.execute(
                config=config,
                params=AuthUserRoleAndPermissions(
                    email=params.email, location=location_entity.id
                ),
            )
        )
        if isinstance(user_role_and_permissions, str):
            return user_role_and_permissions

        permissions, rol_q = user_role_and_permissions

        auth_menu = self.auth_menu_use_case.execute(
            config=config,
            params=AuthMenu(company=company_entity.id, permissions=permissions),
        )

        if isinstance(auth_menu, str):
            return auth_menu

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
                permissions=permissions,
                menu=auth_menu,
            )
        )

        return result
