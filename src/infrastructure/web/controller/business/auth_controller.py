from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.index import AuthLoginRequest
from src.domain.services.use_cases.business.auth.auth_login_use_case import (
    AuthLoginUseCase,
)


class AuthController:
    def __init__(self) -> None:
        self.message = Message()
        self.auth_login_use_case = AuthLoginUseCase()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def login(self, config: Config, params: AuthLoginRequest) -> Response:

        result = self.auth_login_use_case.execute(config=config, params=params)
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_SAVED_INFORMATION.value
                ),
            ),
        )
