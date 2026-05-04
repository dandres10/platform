# SPEC-006 T2
from typing import Optional, Union

from src.core.classes.async_message import Message
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.notifications.send_email_request import (
    SendEmailRequest,
)
from src.domain.services.repositories.external.i_email_service import IEmailService
from src.infrastructure.services.email.email_service_stub import EmailServiceStub


_TEMPLATE_NOT_FOUND_MARKER = "Message not configurated"


def _render_template(template: str, template_vars: dict) -> str:
    rendered = template
    for key, value in (template_vars or {}).items():
        rendered = rendered.replace("{{" + str(key) + "}}", str(value))
    return rendered


class SendEmailUseCase:
    def __init__(self, email_service: Optional[IEmailService] = None):
        self.email_service = email_service or EmailServiceStub()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: SendEmailRequest,
    ) -> Union[bool, str]:
        config.response_type = RESPONSE_TYPE.OBJECT

        original_language = config.language
        if params.language:
            config.language = params.language
        try:
            subject_template = await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=params.subject_key),
            )
            body_template = await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=params.body_key),
            )
        finally:
            config.language = original_language

        if subject_template == _TEMPLATE_NOT_FOUND_MARKER:
            return f"Email subject template not found: {params.subject_key}"
        if body_template == _TEMPLATE_NOT_FOUND_MARKER:
            return f"Email body template not found: {params.body_key}"

        rendered_subject = _render_template(subject_template, params.template_vars or {})
        rendered_body = _render_template(body_template, params.template_vars or {})

        return await self.email_service.send(
            to=params.to,
            subject=rendered_subject,
            body=rendered_body,
        )
