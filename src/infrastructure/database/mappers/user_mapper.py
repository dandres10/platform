
from typing import List
from src.domain.models.entities.user.index import (
    User,
    UserSave,
    UserUpdate,
)
from src.infrastructure.database.entities.user_entity import UserEntity


def map_to_user(user_entity: UserEntity) -> User:
    return User(
        id=user_entity.id,
        rol_id=user_entity.rol_id,
        platform_id=user_entity.platform_id,
        password=user_entity.password,
        email=user_entity.email,
        first_name=user_entity.first_name,
        last_name=user_entity.last_name,
        phone=user_entity.phone,
        refresh_token=user_entity.refresh_token,
        state=user_entity.state,
        created_date=user_entity.created_date,
        updated_date=user_entity.updated_date,
    )

def map_to_list_user(user_entities: List[UserEntity]) -> List[User]:
    return [map_to_user(user) for user in user_entities]

def map_to_user_entity(user: User) -> UserEntity:
    return UserEntity(
        id=user.id,
        rol_id=user.rol_id,
        platform_id=user.platform_id,
        password=user.password,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        refresh_token=user.refresh_token,
        state=user.state,
        created_date=user.created_date,
        updated_date=user.updated_date,
    )

def map_to_list_user_entity(users: List[User]) -> List[UserEntity]:
    return [map_to_user_entity(user) for user in users]

def map_to_save_user_entity(user: UserSave) -> UserEntity:
    return UserEntity(
        rol_id=user.rol_id,
        platform_id=user.platform_id,
        password=user.password,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        state=user.state,
    )

def map_to_update_user_entity(user: UserUpdate) -> UserEntity:
    return UserEntity(
        id=user.id,
        rol_id=user.rol_id,
        platform_id=user.platform_id,
        password=user.password,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        refresh_token=user.refresh_token,
        state=user.state,
    )

