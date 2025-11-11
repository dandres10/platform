from src.domain.models.business.auth.list_users_external import (
    UserExternalItem
)


def map_to_user_external_item(row) -> UserExternalItem:
    return UserExternalItem(
        platform_id=row.platform_id,
        user_id=row.user_id,
        email=row.email,
        identification=row.identification,
        first_name=row.first_name,
        last_name=row.last_name,
        phone=row.phone,
        user_state=row.user_state,
        user_created_date=row.user_created_date,
        user_updated_date=row.user_updated_date,
        language_id=row.language_id,
        currency_id=row.currency_id,
        token_expiration_minutes=row.token_expiration_minutes,
        refresh_token_expiration_minutes=row.refresh_token_expiration_minutes,
        platform_created_date=row.platform_created_date,
        platform_updated_date=row.platform_updated_date,
    )

