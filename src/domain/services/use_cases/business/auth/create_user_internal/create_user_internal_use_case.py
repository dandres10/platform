from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.business.auth.create_user_internal import (
    CreateUserInternalRequest,
    LocationRolItem
)
from src.domain.models.entities.platform.index import PlatformSave, PlatformRead
from src.domain.models.entities.user.index import UserSave
from src.domain.models.entities.user_location_rol.index import UserLocationRolSave
from src.domain.models.entities.language.index import LanguageRead
from src.domain.models.entities.location.index import LocationRead
from src.domain.models.entities.currency.index import CurrencyRead
from src.domain.models.entities.rol.index import RolRead

from src.domain.services.use_cases.entities.language.language_read_use_case import (
    LanguageReadUseCase
)
from src.domain.services.use_cases.entities.location.location_read_use_case import (
    LocationReadUseCase
)
from src.domain.services.use_cases.entities.currency.currency_read_use_case import (
    CurrencyReadUseCase
)
from src.domain.services.use_cases.entities.rol.rol_read_use_case import (
    RolReadUseCase
)
from src.domain.services.use_cases.entities.user.user_list_use_case import (
    UserListUseCase
)

from src.domain.services.use_cases.entities.platform.platform_save_use_case import (
    PlatformSaveUseCase
)
from src.domain.services.use_cases.entities.user.user_save_use_case import (
    UserSaveUseCase
)
from src.domain.services.use_cases.entities.user_location_rol.user_location_rol_save_use_case import (
    UserLocationRolSaveUseCase
)

from src.infrastructure.database.repositories.entities.language_repository import (
    LanguageRepository
)
from src.infrastructure.database.repositories.entities.location_repository import (
    LocationRepository
)
from src.infrastructure.database.repositories.entities.currency_repository import (
    CurrencyRepository
)
from src.infrastructure.database.repositories.entities.rol_repository import (
    RolRepository
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository
)
from src.infrastructure.database.repositories.entities.platform_repository import (
    PlatformRepository
)
from src.infrastructure.database.repositories.entities.user_location_rol_repository import (
    UserLocationRolRepository
)


language_repository = LanguageRepository()
location_repository = LocationRepository()
currency_repository = CurrencyRepository()
rol_repository = RolRepository()
user_repository = UserRepository()
platform_repository = PlatformRepository()
user_location_rol_repository = UserLocationRolRepository()


class CreateUserInternalUseCase:
    def __init__(self):
        self.language_read_uc = LanguageReadUseCase(language_repository)
        self.location_read_uc = LocationReadUseCase(location_repository)
        self.currency_read_uc = CurrencyReadUseCase(currency_repository)
        self.rol_read_uc = RolReadUseCase(rol_repository)
        self.user_list_uc = UserListUseCase(user_repository)

        self.platform_save_uc = PlatformSaveUseCase(platform_repository)
        self.user_save_uc = UserSaveUseCase(user_repository)
        self.user_location_rol_save_uc = UserLocationRolSaveUseCase(
            user_location_rol_repository
        )

        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: CreateUserInternalRequest,
    ) -> Union[str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT


        language = await self.language_read_uc.execute(
            config=config,
            params=LanguageRead(id=params.language_id)
        )
        if isinstance(language, str) or not language:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_LANGUAGE_NOT_FOUND.value
                ),
            )


        currency = await self.currency_read_uc.execute(
            config=config,
            params=CurrencyRead(id=params.currency_id)
        )
        if isinstance(currency, str) or not currency:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_CURRENCY_NOT_FOUND.value
                ),
            )


        if not params.location_rol or len(params.location_rol) == 0:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EMPTY_LOCATION_ROL.value
                ),
            )

        validated_items = []
        seen_combinations = set()

        for item in params.location_rol:
            combination = (str(item.location_id), str(item.rol_id))
            if combination in seen_combinations:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_CREATE_USER_DUPLICATE_COMBINATION.value
                    ),
                )
            seen_combinations.add(combination)


            location = await self.location_read_uc.execute(
                config=config,
                params=LocationRead(id=item.location_id)
            )
            if isinstance(location, str) or not location:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_CREATE_USER_LOCATION_NOT_FOUND.value,
                        params={"location_id": str(item.location_id)}
                    ),
                )


            rol = await self.rol_read_uc.execute(
                config=config,
                params=RolRead(id=item.rol_id)
            )
            if isinstance(rol, str) or not rol:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.AUTH_CREATE_USER_ROL_NOT_FOUND.value,
                        params={"rol_id": str(item.rol_id)}
                    ),
                )

            validated_items.append({
                "location_id": item.location_id,
                "rol_id": item.rol_id,
                "location": location,
                "rol": rol
            })


        existing_users = await self.user_list_uc.execute(
            config=config,
            params=Pagination(
                filters=[
                    FilterManager(
                        field="email",
                        condition=CONDITION_TYPE.EQUALS,
                        value=params.email
                    )
                ]
            )
        )
        if existing_users and not isinstance(existing_users, str):
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_CREATE_USER_EMAIL_ALREADY_EXISTS.value
                ),
            )


        first_location_id = params.location_rol[0].location_id

        platform_created = await self.platform_save_uc.execute(
            config=config,
            params=PlatformSave(
                language_id=params.language_id,
                location_id=first_location_id,
                currency_id=params.currency_id,
                token_expiration_minutes=params.token_expiration_minutes,
                refresh_token_expiration_minutes=params.refresh_token_expiration_minutes
            )
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
                state=True
            )
        )

        if isinstance(user_created, str) or not user_created:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )


        for validated_item in validated_items:
            user_location_rol_created = await self.user_location_rol_save_uc.execute(
                config=config,
                params=UserLocationRolSave(
                    user_id=user_created.id,
                    location_id=validated_item["location_id"],
                    rol_id=validated_item["rol_id"]
                )
            )

            if isinstance(user_location_rol_created, str) or not user_location_rol_created:
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                    ),
                )
        
        return None

