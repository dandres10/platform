# SPEC-006 T5
from typing import List

from src.domain.models.entities.password_reset_token.index import (
    PasswordResetToken,
    PasswordResetTokenSave,
    PasswordResetTokenUpdate,
)
from src.infrastructure.database.entities.password_reset_token_entity import (
    PasswordResetTokenEntity,
)


def map_to_password_reset_token(
    entity: PasswordResetTokenEntity,
) -> PasswordResetToken:
    return PasswordResetToken(
        id=entity.id,
        user_id=entity.user_id,
        token=entity.token,
        expires_at=entity.expires_at,
        used_at=entity.used_at,
        state=entity.state,
        created_date=entity.created_date,
        updated_date=entity.updated_date,
    )


def map_to_list_password_reset_token(
    entities: List[PasswordResetTokenEntity],
) -> List[PasswordResetToken]:
    return [map_to_password_reset_token(e) for e in entities]


def map_to_password_reset_token_entity(
    model: PasswordResetToken,
) -> PasswordResetTokenEntity:
    return PasswordResetTokenEntity(
        id=model.id,
        user_id=model.user_id,
        token=model.token,
        expires_at=model.expires_at,
        used_at=model.used_at,
        state=model.state,
        created_date=model.created_date,
        updated_date=model.updated_date,
    )


def map_to_list_password_reset_token_entity(
    models: List[PasswordResetToken],
) -> List[PasswordResetTokenEntity]:
    return [map_to_password_reset_token_entity(m) for m in models]


def map_to_save_password_reset_token_entity(
    model: PasswordResetTokenSave,
) -> PasswordResetTokenEntity:
    return PasswordResetTokenEntity(
        user_id=model.user_id,
        token=model.token,
        expires_at=model.expires_at,
        state=model.state,
    )


def map_to_update_password_reset_token_entity(
    model: PasswordResetTokenUpdate,
) -> PasswordResetTokenEntity:
    return PasswordResetTokenEntity(
        id=model.id,
        user_id=model.user_id,
        token=model.token,
        expires_at=model.expires_at,
        used_at=model.used_at,
        state=model.state,
    )
