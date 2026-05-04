# SPEC-006 T3
from src.core.classes.async_message import Message
from src.core.config import settings
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.notifications.send_email_request import (
    SendEmailRequest,
)
from src.domain.services.use_cases.business.notifications.send_email_use_case import (
    SendEmailUseCase,
)


class NotificationsController:
    def __init__(self) -> None:
        self.message = Message()
        self.send_email_use_case = SendEmailUseCase()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def send_email(
        self, config: Config, params: SendEmailRequest
    ) -> Response[bool]:
        result = await self.send_email_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(response=False, message=result)

        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_QUERY_MADE.value
                ),
            ),
        )
