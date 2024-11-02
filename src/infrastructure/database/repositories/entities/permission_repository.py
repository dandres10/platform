
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
from src.domain.models.entities.permission.index import (
    Permission,
    PermissionDelete,
    PermissionRead,
    PermissionUpdate,
)
from src.domain.services.repositories.entities.i_permission_repository import (
    IPermissionRepository,
)
from src.infrastructure.database.entities.permission_entity import PermissionEntity
from src.infrastructure.database.mappers.permission_mapper import (
    map_to_permission,
    map_to_list_permission,
)


class PermissionRepository(IPermissionRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: PermissionEntity) -> Union[Permission, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_permission(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: PermissionUpdate) -> Union[Permission, None]:
        async with config.async_db as db:
            stmt = select(PermissionEntity).filter(PermissionEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            permission = result.scalars().first()

            if not permission:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(permission, key, value)

            await db.commit()
            await db.refresh(permission)
            return map_to_permission(permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Permission], None]:
        async with config.async_db as db:
            stmt = select(PermissionEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=PermissionEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            permissions = result.scalars().all()

            if not permissions:
                return None
            return map_to_list_permission(permissions)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: PermissionDelete,
    ) -> Union[Permission, None]:
        async with config.async_db as db:
            stmt = select(PermissionEntity).filter(PermissionEntity.id == params.id)
            result = await db.execute(stmt)
            permission = result.scalars().first()

            if not permission:
                return None

            await db.delete(permission)
            await db.commit()
            return map_to_permission(permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: PermissionRead,
    ) -> Union[Permission, None]:
        async with config.async_db as db:
            stmt = select(PermissionEntity).filter(PermissionEntity.id == params.id)
            result = await db.execute(stmt)
            permission = result.scalars().first()

            if not permission:
                return None

            return map_to_permission(permission)
        