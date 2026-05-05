# SPEC-006 T14
from datetime import datetime, timezone
from typing import Union

from src.core.classes.async_message import Message
from src.core.classes.password import Password
from src.core.config import settings
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.reset_password import (
    ResetPasswordRequest,
)
from src.domain.models.entities.user.index import UserRead, UserUpdate
from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase,
)
from src.domain.services.use_cases.entities.user.user_update_use_case import (
    UserUpdateUseCase,
)
from src.infrastructure.database.repositories.entities.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)


user_repository = UserRepository()
password_reset_token_repository = PasswordResetTokenRepository()


class ResetPasswordUseCase:
    def __init__(self):
        self.user_read_uc = UserReadUseCase(user_repository=user_repository)
        self.user_update_uc = UserUpdateUseCase(user_repository=user_repository)
        self.password_reset_token_repository = password_reset_token_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: ResetPasswordRequest,
    ) -> Union[str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT

        token = await self.password_reset_token_repository.read_by_token(
            config=config, token=params.token
        )
        if token is None:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_RESET_PASSWORD_TOKEN_INVALID.value
                ),
            )

        if token.used_at is not None:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_RESET_PASSWORD_TOKEN_ALREADY_USED.value
                ),
            )

        now = datetime.now(timezone.utc)
        if token.expires_at < now:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_RESET_PASSWORD_TOKEN_EXPIRED.value
                ),
            )

        user = await self.user_read_uc.execute(
            config=config, params=UserRead(id=token.user_id)
        )
        if isinstance(user, str) or user is None:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_RESET_PASSWORD_TOKEN_INVALID.value
                ),
            )

        new_hash = Password.hash_password(password=params.new_password)
        update_result = await self.user_update_uc.execute(
            config=config,
            params=UserUpdate(
                id=user.id,
                platform_id=user.platform_id,
                password=new_hash,
                email=user.email,
                identification=user.identification,
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone,
                refresh_token=None,
                password_changed_at=now,
                state=user.state,
            ),
        )
        if isinstance(update_result, str) or update_result is None:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_UPDATE_FAILED.value
                ),
            )

        await self.password_reset_token_repository.mark_used(
            config=config, id=token.id
        )

        await self.password_reset_token_repository.delete_active_for_user(
            config=config, user_id=user.id
        )

        return None
