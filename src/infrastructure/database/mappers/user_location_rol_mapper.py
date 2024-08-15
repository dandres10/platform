
from typing import List
from src.domain.models.entities.user_location_rol.index import (
    UserLocationRol,
    UserLocationRolSave,
    UserLocationRolUpdate,
)
from src.infrastructure.database.entities.user_location_rol_entity import UserLocationRolEntity


def map_to_user_location_rol(user_location_rol_entity: UserLocationRolEntity) -> UserLocationRol:
    return UserLocationRol(
        id=userlocationrol_entity.id,
        user_id=userlocationrol_entity.user_id,
        location_id=userlocationrol_entity.location_id,
        rol_id=userlocationrol_entity.rol_id,
        state=userlocationrol_entity.state,
        created_date=userlocationrol_entity.created_date,
        updated_date=userlocationrol_entity.updated_date,
    )

def map_to_list_user_location_rol(user_location_rol_entities: List[UserLocationRolEntity]) -> List[UserLocationRol]:
    return [map_to_user_location_rol(user_location_rol) for user_location_rol in user_location_rol_entities]

def map_to_user_location_rol_entity(user_location_rol: UserLocationRol) -> UserLocationRolEntity:
    return UserLocationRolEntity(
        id=userlocationrol.id,
        user_id=userlocationrol.user_id,
        location_id=userlocationrol.location_id,
        rol_id=userlocationrol.rol_id,
        state=userlocationrol.state,
        created_date=userlocationrol.created_date,
        updated_date=userlocationrol.updated_date,
    )

def map_to_list_user_location_rol_entity(user_location_rols: List[UserLocationRol]) -> List[UserLocationRolEntity]:
    return [map_to_user_location_rol_entity(user_location_rol) for user_location_rol in user_location_rols]

def map_to_save_user_location_rol_entity(user_location_rol: UserLocationRolSave) -> UserLocationRolEntity:
    return UserLocationRolEntity(
        user_id=user_location_rol.user_id,
        location_id=user_location_rol.location_id,
        rol_id=user_location_rol.rol_id,
        state=user_location_rol.state,
    )

def map_to_update_user_location_rol_entity(user_location_rol: UserLocationRolUpdate) -> UserLocationRolEntity:
    return UserLocationRolEntity(
        id=user_location_rol.id,
        user_id=user_location_rol.user_id,
        location_id=user_location_rol.location_id,
        rol_id=user_location_rol.rol_id,
        state=user_location_rol.state,
    )

