from typing import List, Union
from src.core.classes.async_message import Message
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.access_token import AccessToken
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_currencies_by_location import (
    AuthCurremciesByLocation,
)
from src.domain.models.business.auth.login.auth_initial_user_data import (
    AuthInitialUserData,
)
from src.domain.models.business.auth.login.auth_locations import AuthLocations
from src.domain.models.business.auth.login.auth_login_response import (
    CompanyLoginResponse,
    CountryLoginResponse,
    CurrencyLoginResponse,
    LanguageLoginResponse,
    LocationLoginResponse,
    PlatformConfiguration,
    PlatformLoginResponse,
    PlatformVariations,
    UserLoginResponse,
)
from src.domain.models.business.auth.login.auth_user_role_and_permissions import (
    AuthUserRoleAndPermissions,
)
from src.domain.models.business.auth.login.companies_by_user import CompaniesByUser
from src.domain.models.business.auth.login.index import (
    AuthLoginRequest,
    AuthLoginResponse,
    AuthMenu,
)
from src.domain.models.entities.company.company import Company
from src.domain.models.entities.user.user_update import UserUpdate
from src.domain.services.use_cases.business.auth.login.auth_currencies_use_case import (
    AuthCurrenciesUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_initial_user_data_use_case import (
    AuthInitialUserDataUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_languages_use_case import (
    AuthLanguagesUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_locations_use_case import (
    AuthLocationsUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_menu_use_case import (
    AuthMenuUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_user_role_and_permissions import (
    AuthUserRoleAndPermissionsUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_validate_user_use_case import (
    AuthValidateUserUseCase,
)
from src.domain.services.use_cases.business.auth.login.companies_by_user_use_case import (
    CompaniesByUserUseCase,
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


class AuthLoginUseCase:
    def __init__(
        self,
    ):
        self.auth_validate_user_use_case = AuthValidateUserUseCase()
        self.user_update_use_case = UserUpdateUseCase(user_repository=user_repository)
        self.auth_languages_use_case = AuthLanguagesUseCase()
        self.auth_locations_use_case = AuthLocationsUseCase()
        self.auth_currencies_use_case = AuthCurrenciesUseCase()
        self.auth_initial_user_data_use_case = AuthInitialUserDataUseCase()
        self.auth_menu_use_case = AuthMenuUseCase()
        self.auth_user_role_and_permissions_use_case = (
            AuthUserRoleAndPermissionsUseCase()
        )
        self.companies_by_user_use_case = CompaniesByUserUseCase()
        self.message = Message()
        self.token = Token()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
    ) -> Union[AuthLoginResponse, str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        user_validator = await self.auth_validate_user_use_case.execute(
            config=config, params=params
        )
        if isinstance(user_validator, str):
            return user_validator

        companies_by_user: List[Company] | str = (
            await self.companies_by_user_use_case.execute(
                config=config, params=CompaniesByUser(email=params.email)
            )
        )

        if isinstance(companies_by_user, str):
            return companies_by_user

        initial_user_data = await self.auth_initial_user_data_use_case.execute(
            config=config, params=AuthInitialUserData(email=params.email)
        )
        if isinstance(initial_user_data, str):
            return initial_user_data

        (
            platform,
            user,
            language,
            location,
            currency,
            country,
            company,
        ) = initial_user_data

        user_role_and_permissions = (
            await self.auth_user_role_and_permissions_use_case.execute(
                config=config,
                params=AuthUserRoleAndPermissions(
                    email=params.email, location=location.id
                ),
            )
        )
        if isinstance(user_role_and_permissions, str):
            return user_role_and_permissions

        permissions, rol_q = user_role_and_permissions

        auth_menu = await self.auth_menu_use_case.execute(
            config=config,
            params=AuthMenu(company=company.id, permissions=permissions),
        )

        if isinstance(auth_menu, str):
            return auth_menu

        currencies = await self.auth_currencies_use_case.execute(
            config=config, params=AuthCurremciesByLocation(location=location.id)
        )

        if isinstance(currencies, str):
            return currencies

        locations = await self.auth_locations_use_case.execute(
            config=config,
            params=AuthLocations(user_id=user.id, company_id=company.id),
        )

        if isinstance(locations, str):
            return locations

        languages = await self.auth_languages_use_case.execute(config=config)

        if isinstance(languages, str):
            return languages

        access_token = AccessToken(
            rol_id=str(rol_q.id),
            rol_code=str(rol_q.code),
            user_id=str(user.id),
            location_id=str(location.id),
            currency_id=str(currency.id),
            company_id=str(company.id),
            token_expiration_minutes=platform.token_expiration_minutes,
            permissions=[permission.name for permission in permissions],
        )

        token = self.token.create_access_token(data=access_token)
        refresh_token = self.token.create_refresh_token(data=access_token)

        user_update = await self.user_update_use_case.execute(
            config=config,
            params=UserUpdate(
                id=user.id,
                platform_id=user.platform_id,
                password=user.password,
                email=user.email,
                identification=user.identification,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                refresh_token=refresh_token,
                state=user.state,
            ),
        )

        if isinstance(user_update, str):
            return user_update

        # SPEC-019: response composition from domain DTOs
        result = AuthLoginResponse(
            platform_configuration=PlatformConfiguration(
                user=UserLoginResponse(
                    id=user.id,
                    email=user.email,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    phone=user.phone,
                    state=user.state,
                ),
                currency=CurrencyLoginResponse(
                    id=currency.id,
                    name=currency.name,
                    code=currency.code,
                    symbol=currency.symbol,
                    state=currency.state,
                ),
                location=LocationLoginResponse(
                    id=location.id,
                    name=location.name,
                    address=location.address,
                    city_id=location.city_id,
                    phone=location.phone,
                    email=location.email,
                    main_location=location.main_location,
                    latitude=location.latitude,
                    longitude=location.longitude,
                    google_place_id=location.google_place_id,
                    state=location.state,
                ),
                language=LanguageLoginResponse(
                    id=language.id,
                    name=language.name,
                    code=language.code,
                    native_name=language.native_name,
                    state=language.state,
                ),
                platform=PlatformLoginResponse(
                    id=platform.id,
                    language_id=platform.language_id,
                    location_id=platform.location_id,
                    token_expiration_minutes=platform.token_expiration_minutes,
                    currency_id=platform.currency_id,
                ),
                country=CountryLoginResponse(
                    id=country.id,
                    name=country.name,
                    code=country.code,
                    phone_code=country.phone_code,
                    state=country.state,
                ),
                company=CompanyLoginResponse(
                    id=company.id,
                    name=company.name,
                    inactivity_time=company.inactivity_time,
                    nit=company.nit,
                    state=company.state,
                ),
                rol=rol_q,
                permissions=permissions,
                menu=auth_menu,
            ),
            platform_variations=PlatformVariations(
                currencies=currencies,
                locations=locations,
                languages=languages,
                companies=companies_by_user,
            ),
            token=token,
        )

        return result
