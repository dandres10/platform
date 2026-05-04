from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.refresh_token.auth_refresh_token_response import (
    AuthRefreshTokenResponse,
)
from src.domain.services.use_cases.business.auth.login.check_user_type_by_rol_use_case import (
    CheckUserTypeByRolUseCase,
)
from src.domain.services.use_cases.business.auth.refresh_token.auth_refresh_token_use_case import (
    AuthRefreshTokenUseCase,
)
from src.domain.services.use_cases.business.auth.refresh_token.auth_refresh_token_external_use_case import (
    AuthRefreshTokenExternalUseCase,
)
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES


class AuthRefreshTokenOrchestratorUseCase:
    """
    Orquestador de refresh token que detecta el tipo de usuario
    y redirige al flujo correspondiente.
    
    Usa el user_id del token para determinar si es interno o externo.
    """
    
    def __init__(self):
        self.check_user_type_by_rol_use_case = CheckUserTypeByRolUseCase()
        self.auth_refresh_token_use_case = AuthRefreshTokenUseCase()
        self.auth_refresh_token_external_use_case = AuthRefreshTokenExternalUseCase()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
    ) -> Union[AuthRefreshTokenResponse, str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        # 1. Obtener user_id del token actual
        user_id = config.token.user_id

        # 2. Detectar tipo de usuario por ROL
        user_type_info = await self.check_user_type_by_rol_use_case.execute(
            config=config, user_id=user_id
        )

        # 3. Si no tiene rol asignado, retornar error
        if user_type_info is None:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND.value
                ),
            )

        # 4. Redirigir al flujo correspondiente basado en el rol
        if user_type_info.is_internal:
            return await self.auth_refresh_token_use_case.execute(config=config)
        else:
            return await self.auth_refresh_token_external_use_case.execute(config=config)
