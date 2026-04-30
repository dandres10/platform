from typing import Union
from src.core.classes.async_message import Message
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.access_token import AccessToken
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_login_response import (
    PlatformConfiguration,
    PlatformVariations,
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
from src.infrastructure.database.repositories.business.mappers.auth.login.login_mapper import (
    map_to_country_login_response,
    map_to_currecy_login_response,
    map_to_language_login_response,
    map_to_platform_login_response,
    map_to_user_login_response,
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

        platform_entity, user_entity, language_entity, currency_entity = initial_data

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
            config=config, user_id=user_entity.id
        )

        # 8. Generar tokens
        access_token = AccessToken(
            rol_id=str(rol_entity.id),
            rol_code=str(rol_entity.code),
            user_id=str(user_entity.id),
            location_id=None,  # Usuario externo no tiene ubicación
            currency_id=str(currency_entity.id),
            company_id=None,   # Usuario externo no tiene compañía
            token_expiration_minutes=platform_entity.token_expiration_minutes,
            permissions=[permission.name for permission in permissions],
        )

        token = self.token.create_access_token(data=access_token)
        refresh_token = self.token.create_refresh_token(data=access_token)

        # 9. Actualizar refresh_token del usuario
        user_update = await self.user_update_use_case.execute(
            config=config,
            params=UserUpdate(
                id=user_entity.id,
                platform_id=user_entity.platform_id,
                password=user_entity.password,
                email=user_entity.email,
                identification=user_entity.identification,
                first_name=user_entity.first_name,
                last_name=user_entity.last_name,
                phone=user_entity.phone,
                refresh_token=refresh_token,
                state=user_entity.state,
            ),
        )

        if isinstance(user_update, str):
            return user_update

        # 10. Construir respuesta
        result = AuthLoginResponse(
            platform_configuration=PlatformConfiguration(
                user=map_to_user_login_response(user_entity=user_entity),
                currency=map_to_currecy_login_response(currency_entity=currency_entity),
                location=None,  # Usuario externo no tiene ubicación
                language=map_to_language_login_response(language_entity=language_entity),
                platform=map_to_platform_login_response(platform_entity=platform_entity),
                country=map_to_country_login_response(country_entity=country_entity) if country_entity else None,
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
