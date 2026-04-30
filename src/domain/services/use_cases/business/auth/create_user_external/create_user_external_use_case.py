from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.rol_type import ROL_TYPE
from src.core.models.config import Config
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.business.auth.create_user_external import (
    CreateUserExternalRequest,
)
from src.domain.models.entities.platform.index import PlatformSave
from src.domain.models.entities.user.index import UserSave
from src.domain.models.entities.language.index import LanguageRead
from src.domain.models.entities.currency.index import CurrencyRead
from src.domain.models.entities.geo_division.index import GeoDivisionRead
from src.domain.models.entities.user_location_rol.index import UserLocationRolSave
from src.domain.models.entities.user_country.index import UserCountrySave

from src.domain.services.use_cases.entities.language.language_read_use_case import (
    LanguageReadUseCase,
)
from src.domain.services.use_cases.entities.currency.currency_read_use_case import (
    CurrencyReadUseCase,
)
from src.domain.services.use_cases.entities.geo_division.geo_division_read_use_case import (
    GeoDivisionReadUseCase,
)
from src.domain.services.use_cases.entities.user.user_list_use_case import (
    UserListUseCase,
)
from src.domain.services.use_cases.entities.platform.platform_save_use_case import (
    PlatformSaveUseCase,
)
from src.domain.services.use_cases.entities.user.user_save_use_case import (
    UserSaveUseCase,
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_save_use_case import (
    UserLocationRolSaveUseCase,
)
from src.domain.services.use_cases.entities.user_country.user_country_save_use_case import (
    UserCountrySaveUseCase,
)

from src.infrastructure.database.repositories.entities.language_repository import (
    LanguageRepository,
)
from src.infrastructure.database.repositories.entities.currency_repository import (
    CurrencyRepository,
)
from src.infrastructure.database.repositories.entities.geo_division_repository import (
    GeoDivisionRepository,
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)
from src.infrastructure.database.repositories.entities.platform_repository import (
    PlatformRepository,
)
from src.infrastructure.database.repositories.entities.user_location_rol_repository import (
    UserLocationRolRepository,
)
from src.infrastructure.database.repositories.entities.user_country_repository import (
    UserCountryRepository,
)
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)


language_repository = LanguageRepository()
currency_repository = CurrencyRepository()
geo_division_repository = GeoDivisionRepository()
user_repository = UserRepository()
platform_repository = PlatformRepository()
user_location_rol_repository = UserLocationRolRepository()
user_country_repository = UserCountryRepository()


class CreateUserExternalUseCase:
    def __init__(self):
        self.language_read_uc = LanguageReadUseCase(language_repository)
        self.currency_read_uc = CurrencyReadUseCase(currency_repository)
        self.geo_division_read_uc = GeoDivisionReadUseCase(geo_division_repository)
        self.user_list_uc = UserListUseCase(user_repository)

        self.platform_save_uc = PlatformSaveUseCase(platform_repository)
        self.user_save_uc = UserSaveUseCase(user_repository)
        self.user_location_rol_save_uc = UserLocationRolSaveUseCase(user_location_rol_repository)
        self.user_country_save_uc = UserCountrySaveUseCase(user_country_repository)
        
        self.auth_repository = AuthRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CreateUserExternalRequest,
    ) -> Union[str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        language = await self.language_read_uc.execute(
            config=config, params=LanguageRead(id=params.language_id)
        )
        if isinstance(language, str) or not language:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_LANGUAGE_NOT_FOUND.value
                ),
            )

        currency = await self.currency_read_uc.execute(
            config=config, params=CurrencyRead(id=params.currency_id)
        )
        if isinstance(currency, str) or not currency:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_CURRENCY_NOT_FOUND.value
                ),
            )

        # Validar country si se proporciona (ahora es un nodo geo_division de tipo COUNTRY)
        if params.country_id:
            country = await self.geo_division_read_uc.execute(
                config=config, params=GeoDivisionRead(id=params.country_id)
            )
            if isinstance(country, str) or not country:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND.value
                    ),
                )

        # SPEC-015 T4
        rol_user = await self.auth_repository.external_rol_and_permissions_by_code(
            config=config, rol_code=ROL_TYPE.USER.value
        )
        if not rol_user:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND.value
                ),
            )

        _permissions, rol = rol_user
        rol_id = rol.id

        existing_users_email = await self.user_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="email",
                        condition=CONDITION_TYPE.EQUALS,
                        value=params.email,
                    )
                ]
            ),
        )
        if existing_users_email and not isinstance(existing_users_email, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_EMAIL_ALREADY_EXISTS.value
                ),
            )

        existing_users_identification = await self.user_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="identification",
                        condition=CONDITION_TYPE.EQUALS,
                        value=params.identification,
                    )
                ]
            ),
        )
        if existing_users_identification and not isinstance(
            existing_users_identification, str
        ):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_IDENTIFICATION_ALREADY_EXISTS.value
                ),
            )

        platform_created = await self.platform_save_uc.execute(
            config=config,
            params=PlatformSave(
                language_id=params.language_id,
                location_id=None,
                currency_id=params.currency_id,
                token_expiration_minutes=params.token_expiration_minutes,
                refresh_token_expiration_minutes=params.refresh_token_expiration_minutes,
            ),
        )

        if isinstance(platform_created, str) or not platform_created:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )

        user_created = await self.user_save_uc.execute(
            config=config,
            params=UserSave(
                platform_id=platform_created.id,
                email=params.email,
                password=params.password,
                identification=params.identification,
                first_name=params.first_name,
                last_name=params.last_name,
                phone=params.phone,
                state=True,
            ),
        )

        if isinstance(user_created, str) or not user_created:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )

        # Crear registro en user_location_rol (con location_id=None para externos)
        user_location_rol_created = await self.user_location_rol_save_uc.execute(
            config=config,
            params=UserLocationRolSave(
                user_id=user_created.id,
                location_id=None,  # Usuario externo no tiene ubicación
                rol_id=rol_id,
                state=True,
            ),
        )

        if isinstance(user_location_rol_created, str) or not user_location_rol_created:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )

        # Crear registro en user_country si se proporciona country_id
        if params.country_id:
            user_country_created = await self.user_country_save_uc.execute(
                config=config,
                params=UserCountrySave(
                    user_id=user_created.id,
                    country_id=params.country_id,
                    state=True,
                ),
            )

            if isinstance(user_country_created, str) or not user_country_created:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                    ),
                )

        return None
