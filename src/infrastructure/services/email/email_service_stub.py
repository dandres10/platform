# SPEC-006 T1
import logging

from src.domain.services.repositories.external.i_email_service import IEmailService


logger = logging.getLogger(__name__)


class EmailServiceStub(IEmailService):
    async def send(self, to: str, subject: str, body: str) -> bool:
        logger.info(
            "[EMAIL STUB] To=%s | Subject=%s | Body=%s",
            to,
            subject,
            body,
        )
        return True
