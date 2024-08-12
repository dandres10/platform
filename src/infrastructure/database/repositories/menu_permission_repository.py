
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.menu_permission.index import (
    MenuPermission,
    MenuPermissionDelete,
    MenuPermissionRead,
    MenuPermissionUpdate,
)
from src.domain.services.repositories.entities.i_menu_permission_repository import (
    IMenuPermissionRepository,
)
from src.infrastructure.database.entities.menu_permission_entity import MenuPermissionEntity
from src.infrastructure.database.mappers.menu_permission_mapper import (
    map_to_menu_permission,
    map_to_list_menu_permission,
)


class MenuPermissionRepository(IMenuPermissionRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: MenuPermissionEntity) -> Union[MenuPermission, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_menu_permission(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: MenuPermissionUpdate) -> Union[MenuPermission, None]:
        db = config.db

        menu_permission: MenuPermissionEntity = (
            db.query(MenuPermissionEntity).filter(MenuPermissionEntity.id == params.id).first()
        )

        if not menu_permission:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(menu_permission, key, value)

        db.commit()
        db.refresh(menu_permission)
        return map_to_menu_permission(menu_permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[MenuPermission], None]:
        db = config.db
        query = db.query(MenuPermissionEntity)

        if params.all_data:
            menu_permissions = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=MenuPermissionEntity
                )
                menu_permissions = query.offset(params.skip).limit(params.limit).all()

        if not menu_permissions:
            return None
        return map_to_list_menu_permission(menu_permissions)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: MenuPermissionDelete,
    ) -> Union[MenuPermission, None]:
        db = config.db
        menu_permission: MenuPermissionEntity = (
            db.query(MenuPermissionEntity).filter(MenuPermissionEntity.id == params.id).first()
        )

        if not menu_permission:
            return None

        db.delete(menu_permission)
        db.commit()
        return map_to_menu_permission(menu_permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: MenuPermissionRead,
    ) -> Union[MenuPermission, None]:
        db = config.db
        menu_permission: MenuPermissionEntity = (
            db.query(MenuPermissionEntity).filter(MenuPermissionEntity.id == params.id).first()
        )

        if not menu_permission:
            return None

        return map_to_menu_permission(menu_permission)
        