# SPEC-006 T13
import logging
from datetime import datetime, timedelta, timezone
from typing import Union
from uuid import uuid4

from src.core.classes.async_message import Message
from src.core.config import settings
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.filter import FilterManager, Pagination
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.forgot_password import (
    ForgotPasswordRequest,
)
from src.domain.models.business.notifications.send_email_request import (
    SendEmailRequest,
)
from src.domain.models.entities.password_reset_token.index import (
    PasswordResetTokenSave,
)
from src.domain.services.use_cases.business.notifications.send_email_use_case import (
    SendEmailUseCase,
)
from src.domain.services.use_cases.entities.user.user_list_use_case import (
    UserListUseCase,
)
from src.infrastructure.database.repositories.entities.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)


logger = logging.getLogger(__name__)


user_repository = UserRepository()
password_reset_token_repository = PasswordResetTokenRepository()


# SPEC-006 T13 — TTL del token (1 hora, OQ4)
RESET_TOKEN_TTL_MINUTES = 60


class ForgotPasswordUseCase:
    def __init__(self):
        self.user_list_uc = UserListUseCase(user_repository)
        self.password_reset_token_repository = password_reset_token_repository
        self.send_email_uc = SendEmailUseCase()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: ForgotPasswordRequest,
    ) -> Union[str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        users = await self.user_list_uc.execute(
            config=config,
            params=Pagination(
                all_data=True,
                filters=[
                    FilterManager(
                        field="email",
                        condition=CONDITION_TYPE.EQUALS.value,
                        value=str(params.email),
                    )
                ],
            ),
        )

        if isinstance(users, list) and len(users) == 1:
            user = users[0]
            token_value = uuid4().hex
            expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
                minutes=RESET_TOKEN_TTL_MINUTES
            )

            saved = await self.password_reset_token_repository.save(
                config=config,
                params=PasswordResetTokenSave(
                    user_id=user.id,
                    token=token_value,
                    expires_at=expires_at,
                ),
            )

            if saved is not None:
                full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                reset_link = (
                    f"{params.reset_link_base}?token={token_value}"
                    if params.reset_link_base
                    else f"https://app.goluti.com/reset-password?token={token_value}"
                )
                try:
                    await self.send_email_uc.execute(
                        config=config,
                        params=SendEmailRequest(
                            to=str(params.email),
                            subject_key=KEYS_MESSAGES.EMAIL_RESET_PASSWORD_SUBJECT.value,
                            body_key=KEYS_MESSAGES.EMAIL_RESET_PASSWORD_BODY.value,
                            template_vars={
                                "name": full_name or "user",
                                "reset_link": reset_link,
                            },
                        ),
                    )
                except Exception as e:
                    logger.warning(
                        "reset email send failed for user %s: %s",
                        user.id,
                        e,
                    )

        return None
