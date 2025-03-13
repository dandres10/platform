from typing import List, Union
from datetime import datetime, timezone
from src.core.classes.token import Token
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.access_token_api import AccessTokenApi
from src.core.models.config import Config
from src.core.models.filter import FilterManager, Pagination
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.create_api_token.create_api_token_request import (
    CreateApiTokenRequest,
)
from src.domain.models.business.auth.create_api_token.create_api_token_response import (
    CreateApiTokenResponse,
)
from src.core.config import settings
from src.domain.models.entities.api_token.api_token import ApiToken
from src.domain.models.entities.api_token.api_token_read import ApiTokenRead
from src.domain.models.entities.api_token.api_token_save import ApiTokenSave
from src.domain.models.entities.rol.rol_read import RolRead
from src.domain.services.repositories.entities.i_rol_repository import IRolRepository
from src.domain.services.use_cases.entities.api_token.api_token_list_use_case import (
    ApiTokenListUseCase,
)
from src.domain.services.use_cases.entities.api_token.api_token_read_use_case import (
    ApiTokenReadUseCase,
)
from src.domain.services.use_cases.entities.api_token.api_token_save_use_case import (
    ApiTokenSaveUseCase,
)
from src.domain.services.use_cases.entities.rol.rol_read_use_case import RolReadUseCase
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)

from src.core.classes.async_message import Message
from src.infrastructure.database.repositories.entities.api_token_repository import (
    ApiTokenRepository,
)
from src.infrastructure.database.repositories.entities.rol_repository import RolRepository

api_token_repository = ApiTokenRepository()
rol_repository = RolRepository()


class CreateApiTokenUseCase:
    def __init__(
        self,
    ):
        self.auth_repository = AuthRepository()
        self.message = Message()
        self.token = Token()
        self.api_token_save_use_case = ApiTokenSaveUseCase(
            api_token_repository=api_token_repository
        )
        self.api_token_list_use_case = ApiTokenListUseCase(
            api_token_repository=api_token_repository
        )

        self.rol_read_use_case = RolReadUseCase(rol_repository=rol_repository)

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(self, config: Config, params: CreateApiTokenRequest) -> Union[
        CreateApiTokenResponse,
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT

        rol_read = await self.rol_read_use_case.execute(
            config=config, params=RolRead(id=params.rol_id)
        )

        if isinstance(rol_read, str):
            return "El rol no existe"

        api_token_list: List[ApiToken] | str = (
            await self.api_token_list_use_case.execute(
                config=config,
                params=Pagination(
                    all_data=True,
                    filters=[
                        FilterManager(
                            field="rol_id",
                            condition=CONDITION_TYPE.EQUALS.value,
                            value=params.rol_id,
                        )
                    ],
                ),
            )
        )

        if not isinstance(api_token_list, str):
            return "El rol ya tiene un token api"

        result: CreateApiTokenResponse | None = (
            await self.auth_repository.create_api_token(config=config, params=params)
        )

        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                ),
            )

        token_api = self.token.create_access_token_api(
            data=AccessTokenApi(
                rol_id=str(result.rol_id),
                rol_code=result.rol_code,
                permissions=result.permissions,
                date=str(datetime.now(timezone.utc)),
            )
        )

        api_token_save: ApiToken | str = await self.api_token_save_use_case.execute(
            config=config,
            params=ApiTokenSave(rol_id=params.rol_id, token=token_api, state=True),
        )

        if isinstance(api_token_save, str):
            return api_token_save

        return result
