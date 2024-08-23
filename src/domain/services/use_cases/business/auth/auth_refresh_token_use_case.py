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
from src.domain.models.business.auth.auth_refresh_token_response import (
    AuthRefreshTokenResponse,
)
from src.domain.models.business.auth.auth_user_role_and_permissions import (
    AuthUserRoleAndPermissions,
)
from src.domain.models.business.auth.index import (
    AuthMenu,
)
from src.domain.models.entities.user.user_read import UserRead
from src.domain.models.entities.user.user_update import UserUpdate
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
from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase,
)
from src.domain.services.use_cases.entities.user.user_update_use_case import (
    UserUpdateUseCase,
)
from src.core.config import settings
from src.core.classes.token import Token
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)


user_repository = UserRepository()


class AuthRefreshTokenUseCase:
    def __init__(
        self,
    ):
        self.auth_validate_user_use_case = AuthValidateUserUseCase()
        self.user_update_use_case = UserUpdateUseCase(user_repository=user_repository)
        self.user_read_use_case = UserReadUseCase(user_repository=user_repository)
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
    ) -> Union[AuthRefreshTokenResponse, str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        user_read = self.user_read_use_case.execute(
            config=config, params=UserRead(id=config.token.user_id)
        )

        if isinstance(user_read, str):
            return user_read

        initial_user_data = self.auth_initial_user_data_use_case.execute(
            config=config, params=AuthInitialUserData(email=user_read.email)
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
                    email=user_read.email, location=location_entity.id
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

        access_token = AccessToken(
            rol_id=str(rol_q.id),
            rol_code=str(rol_q.code),
            user_id=str(user_entity.id),
            location_id=str(location_entity.id),
            currency_id=str(currency_entity.id),
            company_id=str(company_entity.id),
            token_expiration_minutes=platform_entity.token_expiration_minutes,
            permissions=[permission.name for permission in permissions],
        )

        token = self.token.refresh_access_token(
            refresh_token=user_read.refresh_token, data=access_token
        )
        refresh_token = self.token.create_refresh_token(data=access_token)

        user_update = self.user_update_use_case.execute(
            config=config,
            params=UserUpdate(
                id=user_entity.id,
                platform_id=user_entity.platform_id,
                password=user_entity.password,
                email=user_entity.email,
                first_name=user_entity.first_name,
                last_name=user_entity.last_name,
                phone=user_entity.phone,
                refresh_token=refresh_token,
                state=user_entity.state,
            ),
        )

        if isinstance(user_update, str):
            return user_update

        result = AuthRefreshTokenResponse(token=token)

        return result
