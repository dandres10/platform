
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
from src.domain.models.entities.rol_permission.index import (
    RolPermission,
    RolPermissionDelete,
    RolPermissionRead,
    RolPermissionUpdate,
)
from src.domain.services.repositories.entities.i_rol_permission_repository import (
    IRolPermissionRepository,
)
from src.infrastructure.database.entities.rol_permission_entity import RolPermissionEntity
from src.infrastructure.database.mappers.rol_permission_mapper import (
    map_to_rol_permission,
    map_to_list_rol_permission,
)


class RolPermissionRepository(IRolPermissionRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: RolPermissionEntity) -> Union[RolPermission, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_rol_permission(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: RolPermissionUpdate) -> Union[RolPermission, None]:
        async with config.async_db as db:
            stmt = select(RolPermissionEntity).filter(RolPermissionEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            rol_permission = result.scalars().first()

            if not rol_permission:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(rol_permission, key, value)

            await db.commit()
            await db.refresh(rol_permission)
            return map_to_rol_permission(rol_permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[RolPermission], None]:
        async with config.async_db as db:
            stmt = select(RolPermissionEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=RolPermissionEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            rol_permissions = result.scalars().all()

            if not rol_permissions:
                return None
            return map_to_list_rol_permission(rol_permissions)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: RolPermissionDelete,
    ) -> Union[RolPermission, None]:
        async with config.async_db as db:
            stmt = select(RolPermissionEntity).filter(RolPermissionEntity.id == params.id)
            result = await db.execute(stmt)
            rol_permission = result.scalars().first()

            if not rol_permission:
                return None

            await db.delete(rol_permission)
            await db.commit()
            return map_to_rol_permission(rol_permission)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: RolPermissionRead,
    ) -> Union[RolPermission, None]:
        async with config.async_db as db:
            stmt = select(RolPermissionEntity).filter(RolPermissionEntity.id == params.id)
            result = await db.execute(stmt)
            rol_permission = result.scalars().first()

            if not rol_permission:
                return None

            return map_to_rol_permission(rol_permission)
        