from typing import List, Union
from src.core.classes.message import Message
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.access_token import AccessToken
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.auth_currencies_by_location import (
    AuthCurremciesByLocation,
)
from src.domain.models.business.auth.auth_initial_user_data import AuthInitialUserData
from src.domain.models.business.auth.auth_locations import AuthLocations
from src.domain.models.business.auth.auth_login_response import (
    PlatformConfiguration,
    PlatformVariations,
)
from src.domain.models.business.auth.auth_user_role_and_permissions import (
    AuthUserRoleAndPermissions,
)
from src.domain.models.business.auth.index import (
    AuthLoginRequest,
    AuthLoginResponse,
    AuthMenu,
)
from src.domain.services.use_cases.business.auth.auth_currencies_use_case import (
    AuthCurrenciesUseCase,
)
from src.domain.services.use_cases.business.auth.auth_initial_user_data_use_case import (
    AuthInitialUserDataUseCase,
)
from src.domain.services.use_cases.business.auth.auth_languages_use_case import (
    AuthLanguagesUseCase,
)
from src.domain.services.use_cases.business.auth.auth_locations_use_case import (
    AuthLocationsUseCase,
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
    map_to_permission_token_response,
    map_to_platform_login_response,
    map_to_rol_login_response,
    map_to_user_login_response,
)
from src.core.config import settings
from src.core.classes.token import Token


class AuthLoginUseCase:
    def __init__(
        self,
    ):
        self.auth_validate_user_use_case = AuthValidateUserUseCase()
        self.auth_languages_use_case = AuthLanguagesUseCase()
        self.auth_locations_use_case = AuthLocationsUseCase()
        self.auth_currencies_use_case = AuthCurrenciesUseCase()
        self.auth_initial_user_data_use_case = AuthInitialUserDataUseCase()
        self.auth_menu_use_case = AuthMenuUseCase()
        self.auth_user_role_and_permissions_use_case = (
            AuthUserRoleAndPermissionsUseCase()
        )
        self.message = Message()
        self.token = Token()

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

        currencies = self.auth_currencies_use_case.execute(
            config=config, params=AuthCurremciesByLocation(location=location_entity.id)
        )

        if isinstance(currencies, str):
            return currencies

        locations = self.auth_locations_use_case.execute(
            config=config,
            params=AuthLocations(user_id=user_entity.id, company_id=company_entity.id),
        )

        if isinstance(locations, str):
            return locations

        languages = self.auth_languages_use_case.execute(config=config)

        if isinstance(languages, str):
            return languages

        token = self.token.create_access_token(
            data=AccessToken(
                rol_id=str(rol_q.id),
                rol_code=str(rol_q.code),
                user_id=str(user_entity.id),
                location_id=str(location_entity.id),
                currency_id=str(currency_entity.id),
                company_id=str(company_entity.id),
                token_expiration_minutes=platform_entity.token_expiration_minutes,
                permissions=[permission.name for permission in permissions],
            )
        )

        result = AuthLoginResponse(
            platform_configuration=PlatformConfiguration(
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
            ),
            platform_variations=PlatformVariations(
                currencies=currencies, locations=locations, languages=languages
            ),
            token=token,
        )

        return result
