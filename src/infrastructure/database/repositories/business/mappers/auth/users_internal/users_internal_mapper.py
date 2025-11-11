from src.domain.models.business.auth.list_users_by_location import (
    UserByLocationItem
)


def map_to_user_by_location_item(row) -> UserByLocationItem:
    return UserByLocationItem(
        user_location_rol_id=row.user_location_rol_id,
        location_id=row.location_id,
        user_id=row.user_id,
        email=row.email,
        identification=row.identification,
        first_name=row.first_name,
        last_name=row.last_name,
        phone=row.phone,
        user_state=row.user_state,
        user_created_date=row.user_created_date,
        user_updated_date=row.user_updated_date,
        rol_id=row.rol_id,
        rol_name=row.rol_name,
        rol_code=row.rol_code,
        rol_description=row.rol_description,
    )

