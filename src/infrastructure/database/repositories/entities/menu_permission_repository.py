
from pydantic import UUID4
from datetime import datetime
from typing import List, Union
from src.core.config import settings
from sqlalchemy.future import select
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.methods.get_filter import get_filter
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
    async def save(self, config: Config, params: MenuPermissionEntity) -> Union[MenuPermission, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_menu_permission(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: MenuPermissionUpdate) -> Union[MenuPermission, None]:
        async with config.async_db as db:
            stmt = select(MenuPermissionEntity).filter(MenuPermissionEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            menu_permission = result.scalars().first()

            if not menu_permission:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(menu_permission, key, value)

            await db.commit()
            await db.refresh(menu_permission)
            return map_to_menu_permission(menu_permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[MenuPermission], None]:
        async with config.async_db as db:
            stmt = select(MenuPermissionEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=MenuPermissionEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            menu_permissions = result.scalars().all()

            if not menu_permissions:
                return None
            return map_to_list_menu_permission(menu_permissions)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: MenuPermissionDelete,
    ) -> Union[MenuPermission, None]:
        async with config.async_db as db:
            stmt = select(MenuPermissionEntity).filter(MenuPermissionEntity.id == params.id)
            result = await db.execute(stmt)
            menu_permission = result.scalars().first()

            if not menu_permission:
                return None

            await db.delete(menu_permission)
            await db.commit()
            return map_to_menu_permission(menu_permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: MenuPermissionRead,
    ) -> Union[MenuPermission, None]:
        async with config.async_db as db:
            stmt = select(MenuPermissionEntity).filter(MenuPermissionEntity.id == params.id)
            result = await db.execute(stmt)
            menu_permission = result.scalars().first()

            if not menu_permission:
                return None

            return map_to_menu_permission(menu_permission)
        