
from typing import List
from src.domain.models.entities.rol_permission.index import (
    RolPermission,
    RolPermissionSave,
    RolPermissionUpdate,
)
from src.infrastructure.database.entities.rol_permission_entity import RolPermissionEntity


def map_to_rol_permission(rol_permission_entity: RolPermissionEntity) -> RolPermission:
    return RolPermission(
        id=rol_permission_entity.id,
        rol_id=rol_permission_entity.rol_id,
        permission_id=rol_permission_entity.permission_id,
        state=rol_permission_entity.state,
        created_date=rol_permission_entity.created_date,
        updated_date=rol_permission_entity.updated_date,
    )

def map_to_list_rol_permission(rol_permission_entities: List[RolPermissionEntity]) -> List[RolPermission]:
    return [map_to_rol_permission(rol_permission) for rol_permission in rol_permission_entities]

def map_to_rol_permission_entity(rol_permission: RolPermission) -> RolPermissionEntity:
    return RolPermissionEntity(
        id=rol_permission.id,
        rol_id=rol_permission.rol_id,
        permission_id=rol_permission.permission_id,
        state=rol_permission.state,
        created_date=rol_permission.created_date,
        updated_date=rol_permission.updated_date,
    )

def map_to_list_rol_permission_entity(rol_permissions: List[RolPermission]) -> List[RolPermissionEntity]:
    return [map_to_rol_permission_entity(rol_permission) for rol_permission in rol_permissions]

def map_to_save_rol_permission_entity(rol_permission: RolPermissionSave) -> RolPermissionEntity:
    return RolPermissionEntity(
        rol_id=rol_permission.rol_id,
        permission_id=rol_permission.permission_id,
        state=rol_permission.state,
    )

def map_to_update_rol_permission_entity(rol_permission: RolPermissionUpdate) -> RolPermissionEntity:
    return RolPermissionEntity(
        id=rol_permission.id,
        rol_id=rol_permission.rol_id,
        permission_id=rol_permission.permission_id,
        state=rol_permission.state,
    )

