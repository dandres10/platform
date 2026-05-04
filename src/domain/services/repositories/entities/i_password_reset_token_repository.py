# SPEC-006 T6
from abc import ABC, abstractmethod
from typing import List, Optional, Union
from uuid import UUID

from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.domain.models.entities.password_reset_token.index import (
    PasswordResetToken,
    PasswordResetTokenDelete,
    PasswordResetTokenRead,
    PasswordResetTokenSave,
    PasswordResetTokenUpdate,
)


class IPasswordResetTokenRepository(ABC):
    @abstractmethod
    async def save(
        self,
        config: Config,
        params: PasswordResetTokenSave,
    ) -> Union[PasswordResetToken, None]:
        pass

    @abstractmethod
    async def update(
        self,
        config: Config,
        params: PasswordResetTokenUpdate,
    ) -> Union[PasswordResetToken, None]:
        pass

    @abstractmethod
    async def list(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[PasswordResetToken], None]:
        pass

    @abstractmethod
    async def delete(
        self,
        config: Config,
        params: PasswordResetTokenDelete,
    ) -> Union[PasswordResetToken, None]:
        pass

    @abstractmethod
    async def read(
        self,
        config: Config,
        params: PasswordResetTokenRead,
    ) -> Union[PasswordResetToken, None]:
        pass

    @abstractmethod
    async def read_by_token(
        self,
        config: Config,
        token: str,
    ) -> Optional[PasswordResetToken]:
        pass

    @abstractmethod
    async def mark_used(
        self,
        config: Config,
        id: UUID,
    ) -> Optional[PasswordResetToken]:
        pass

    @abstractmethod
    async def delete_active_for_user(
        self,
        config: Config,
        user_id: UUID,
    ) -> int:
        pass
