
from typing import List
from src.domain.models.entities.menu_permission.index import (
    MenuPermission,
    MenuPermissionSave,
    MenuPermissionUpdate,
)
from src.infrastructure.database.entities.menu_permission_entity import MenuPermissionEntity


def map_to_menu_permission(menu_permission_entity: MenuPermissionEntity) -> MenuPermission:
    return MenuPermission(
        id=menu_permission_entity.id,
        menu_id=menu_permission_entity.menu_id,
        permission_id=menu_permission_entity.permission_id,
        state=menu_permission_entity.state,
        created_date=menu_permission_entity.created_date,
        updated_date=menu_permission_entity.updated_date,
    )

def map_to_list_menu_permission(menu_permission_entities: List[MenuPermissionEntity]) -> List[MenuPermission]:
    return [map_to_menu_permission(menu_permission) for menu_permission in menu_permission_entities]

def map_to_menu_permission_entity(menu_permission: MenuPermission) -> MenuPermissionEntity:
    return MenuPermissionEntity(
        id=menu_permission.id,
        menu_id=menu_permission.menu_id,
        permission_id=menu_permission.permission_id,
        state=menu_permission.state,
        created_date=menu_permission.created_date,
        updated_date=menu_permission.updated_date,
    )

def map_to_list_menu_permission_entity(menu_permissions: List[MenuPermission]) -> List[MenuPermissionEntity]:
    return [map_to_menu_permission_entity(menu_permission) for menu_permission in menu_permissions]

def map_to_save_menu_permission_entity(menu_permission: MenuPermissionSave) -> MenuPermissionEntity:
    return MenuPermissionEntity(
        menu_id=menu_permission.menu_id,
        permission_id=menu_permission.permission_id,
        state=menu_permission.state,
    )

def map_to_update_menu_permission_entity(menu_permission: MenuPermissionUpdate) -> MenuPermissionEntity:
    return MenuPermissionEntity(
        id=menu_permission.id,
        menu_id=menu_permission.menu_id,
        permission_id=menu_permission.permission_id,
        state=menu_permission.state,
    )

