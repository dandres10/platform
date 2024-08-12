
from typing import List
from src.domain.models.entities.permission.index import (
    Permission,
    PermissionSave,
    PermissionUpdate,
)
from src.infrastructure.database.entities.permission_entity import PermissionEntity


def map_to_permission(permission_entity: PermissionEntity) -> Permission:
    return Permission(
        id=permission_entity.id,
        company_id=permission_entity.company_id,
        name=permission_entity.name,
        description=permission_entity.description,
        state=permission_entity.state,
        created_date=permission_entity.created_date,
        updated_date=permission_entity.updated_date,
    )

def map_to_list_permission(permission_entities: List[PermissionEntity]) -> List[Permission]:
    return [map_to_permission(permission) for permission in permission_entities]

def map_to_permission_entity(permission: Permission) -> PermissionEntity:
    return PermissionEntity(
        id=permission.id,
        company_id=permission.company_id,
        name=permission.name,
        description=permission.description,
        state=permission.state,
        created_date=permission.created_date,
        updated_date=permission.updated_date,
    )

def map_to_list_permission_entity(permissions: List[Permission]) -> List[PermissionEntity]:
    return [map_to_permission_entity(permission) for permission in permissions]

def map_to_save_permission_entity(permission: PermissionSave) -> PermissionEntity:
    return PermissionEntity(
        company_id=permission.company_id,
        name=permission.name,
        description=permission.description,
        state=permission.state,
    )

def map_to_update_permission_entity(permission: PermissionUpdate) -> PermissionEntity:
    return PermissionEntity(
        id=permission.id,
        company_id=permission.company_id,
        name=permission.name,
        description=permission.description,
        state=permission.state,
    )

