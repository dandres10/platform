from typing import Union
from src.core.classes.async_message import Message
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.access_token import AccessToken
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_login_response import (
    CountryLoginResponse,
    CurrencyLoginResponse,
    LanguageLoginResponse,
    PlatformConfiguration,
    PlatformLoginResponse,
    PlatformVariations,
    UserLoginResponse,
)
from src.domain.models.business.auth.login.index import (
    AuthLoginRequest,
    AuthLoginResponse,
)
from src.domain.models.entities.user.user_update import UserUpdate
from src.domain.services.use_cases.business.auth.login.auth_initial_external_user_data_use_case import (
    AuthInitialExternalUserDataUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_external_rol_and_permissions_use_case import (
    AuthExternalRolAndPermissionsUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_menu_external_use_case import (
    AuthMenuExternalUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_currencies_external_use_case import (
    AuthCurrenciesExternalUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_languages_use_case import (
    AuthLanguagesUseCase,
)
from src.domain.services.use_cases.entities.user.user_update_use_case import (
    UserUpdateUseCase,
)
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.core.config import settings
from src.core.classes.token import Token
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)


user_repository = UserRepository()


class AuthLoginExternalUseCase:
    """
    Flujo de login para usuarios externos.
    
    A diferencia del flujo interno:
    - No tiene company ni location
    - Tiene country desde user_country
    - Obtiene todas las currencies globales
    - Usa menús con type='EXTERNAL'
    - Rol: USER
    """
    
    def __init__(self):
        self.auth_initial_external_user_data_use_case = AuthInitialExternalUserDataUseCase()
        self.auth_external_rol_and_permissions_use_case = AuthExternalRolAndPermissionsUseCase()
        self.auth_menu_external_use_case = AuthMenuExternalUseCase()
        self.auth_currencies_external_use_case = AuthCurrenciesExternalUseCase()
        self.auth_languages_use_case = AuthLanguagesUseCase()
        self.auth_repository = AuthRepository()
        self.user_update_use_case = UserUpdateUseCase(user_repository=user_repository)
        self.message = Message()
        self.token = Token()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: AuthLoginRequest,
        validated_user=None,  # Usuario ya validado por el orquestador
    ) -> Union[AuthLoginResponse, str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        # 1. Obtener datos iniciales del usuario externo
        initial_data = await self.auth_initial_external_user_data_use_case.execute(
            config=config, email=params.email
        )
        if isinstance(initial_data, str):
            return initial_data

        platform, user, language, currency = initial_data

        # 2. Obtener rol USER y permisos
        rol_and_permissions = await self.auth_external_rol_and_permissions_use_case.execute(
            config=config
        )
        if isinstance(rol_and_permissions, str):
            return rol_and_permissions

        permissions, rol_entity = rol_and_permissions

        # 3. Obtener menú externo filtrado por permisos del rol USER
        auth_menu = await self.auth_menu_external_use_case.execute(
            config=config, permissions=permissions
        )
        if isinstance(auth_menu, str):
            return auth_menu

        # 4. Obtener idiomas disponibles
        languages = await self.auth_languages_use_case.execute(config=config)
        if isinstance(languages, str):
            return languages

        # 5. Obtener todas las currencies disponibles
        currencies = await self.auth_currencies_external_use_case.execute(config=config)
        if isinstance(currencies, str):
            return currencies

        # 6. Obtener country del usuario desde user_country (puede ser None)
        country_entity = await self.auth_repository.user_country(
            config=config, user_id=user.id
        )

        # 8. Generar tokens
        access_token = AccessToken(
            rol_id=str(rol_entity.id),
            rol_code=str(rol_entity.code),
            user_id=str(user.id),
            location_id=None,  # Usuario externo no tiene ubicación
            currency_id=str(currency.id),
            company_id=None,   # Usuario externo no tiene compañía
            token_expiration_minutes=platform.token_expiration_minutes,
            permissions=[permission.name for permission in permissions],
            # SPEC-006 T10
            password_changed_at=user.password_changed_at,
        )

        token = self.token.create_access_token(data=access_token)
        refresh_token = self.token.create_refresh_token(data=access_token)

        # 9. Actualizar refresh_token del usuario
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

        # 10. SPEC-019: response composition from domain DTOs
        country_response = (
            CountryLoginResponse(
                id=country_entity.id,
                name=country_entity.name,
                code=country_entity.code,
                phone_code=country_entity.phone_code,
                state=country_entity.state,
            )
            if country_entity
            else None
        )

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
                location=None,  # Usuario externo no tiene ubicación
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
                country=country_response,
                company=None,   # Usuario externo no tiene compañía
                rol=rol_entity,
                permissions=permissions,
                menu=auth_menu,
            ),
            platform_variations=PlatformVariations(
                currencies=currencies,   # Todas las currencies globales
                locations=[],            # Usuario externo no tiene ubicaciones
                languages=languages,
                companies=[],            # Usuario externo no tiene compañías
            ),
            token=token,
        )

        return result
