# SPEC-006 T6
from datetime import datetime, timezone
from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import update as sa_update
from sqlalchemy.future import select

from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.password_reset_token.index import (
    PasswordResetToken,
    PasswordResetTokenDelete,
    PasswordResetTokenRead,
    PasswordResetTokenSave,
    PasswordResetTokenUpdate,
)
from src.domain.services.repositories.entities.i_password_reset_token_repository import (
    IPasswordResetTokenRepository,
)
from src.infrastructure.database.entities.password_reset_token_entity import (
    PasswordResetTokenEntity,
)
from src.infrastructure.database.mappers.password_reset_token_mapper import (
    map_to_list_password_reset_token,
    map_to_password_reset_token,
    map_to_save_password_reset_token_entity,
)


class PasswordResetTokenRepository(IPasswordResetTokenRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(
        self, config: Config, params: PasswordResetTokenSave
    ) -> Union[PasswordResetToken, None]:
        db = config.async_db
        entity = map_to_save_password_reset_token_entity(params)
        db.add(entity)
        await db.flush()
        await db.refresh(entity)
        return map_to_password_reset_token(entity)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(
        self, config: Config, params: PasswordResetTokenUpdate
    ) -> Union[PasswordResetToken, None]:
        db = config.async_db
        stmt = select(PasswordResetTokenEntity).filter(
            PasswordResetTokenEntity.id == params.id
        )
        result = await db.execute(stmt)
        entity = result.scalars().first()

        if not entity:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(entity, key, value)

        await db.flush()
        await db.refresh(entity)
        return map_to_password_reset_token(entity)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(
        self, config: Config, params: Pagination
    ) -> Union[List[PasswordResetToken], None]:
        db = config.async_db
        stmt = select(PasswordResetTokenEntity)

        if params.filters:
            stmt = get_filter(
                query=stmt,
                filters=params.filters,
                entity=PasswordResetTokenEntity,
            )

        if not params.all_data:
            stmt = stmt.offset(params.skip).limit(params.limit)

        result = await db.execute(stmt)
        entities = result.scalars().all()

        if not entities:
            return None
        return map_to_list_password_reset_token(entities)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self, config: Config, params: PasswordResetTokenDelete
    ) -> Union[PasswordResetToken, None]:
        db = config.async_db
        stmt = select(PasswordResetTokenEntity).filter(
            PasswordResetTokenEntity.id == params.id
        )
        result = await db.execute(stmt)
        entity = result.scalars().first()

        if not entity:
            return None

        await db.delete(entity)
        await db.flush()
        return map_to_password_reset_token(entity)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self, config: Config, params: PasswordResetTokenRead
    ) -> Union[PasswordResetToken, None]:
        db = config.async_db
        stmt = select(PasswordResetTokenEntity).filter(
            PasswordResetTokenEntity.id == params.id
        )
        result = await db.execute(stmt)
        entity = result.scalars().first()

        if not entity:
            return None
        return map_to_password_reset_token(entity)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read_by_token(
        self, config: Config, token: str
    ) -> Optional[PasswordResetToken]:
        db = config.async_db
        stmt = select(PasswordResetTokenEntity).filter(
            PasswordResetTokenEntity.token == token
        )
        result = await db.execute(stmt)
        entity = result.scalars().first()

        if not entity:
            return None
        return map_to_password_reset_token(entity)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def mark_used(
        self, config: Config, id: UUID
    ) -> Optional[PasswordResetToken]:
        db = config.async_db
        stmt = select(PasswordResetTokenEntity).filter(
            PasswordResetTokenEntity.id == id
        )
        result = await db.execute(stmt)
        entity = result.scalars().first()

        if not entity:
            return None

        entity.used_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await db.flush()
        await db.refresh(entity)
        return map_to_password_reset_token(entity)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete_active_for_user(
        self, config: Config, user_id: UUID
    ) -> int:
        db = config.async_db
        stmt = (
            sa_update(PasswordResetTokenEntity)
            .where(
                PasswordResetTokenEntity.user_id == user_id,
                PasswordResetTokenEntity.used_at.is_(None),
            )
            .values(used_at=datetime.now(timezone.utc).replace(tzinfo=None))
        )
        result = await db.execute(stmt)
        await db.flush()
        return result.rowcount or 0
