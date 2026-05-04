
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
from src.domain.models.entities.rol.index import (
    Rol,
    RolDelete,
    RolRead,
    RolSave,
    RolUpdate,
)
from src.domain.services.repositories.entities.i_rol_repository import (
    IRolRepository,
)
from src.infrastructure.database.entities.rol_entity import RolEntity
from src.infrastructure.database.mappers.rol_mapper import (
    map_to_rol,
    map_to_list_rol,
    map_to_save_rol_entity,
)


class RolRepository(IRolRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: RolSave) -> Union[Rol, None]:
        db = config.async_db
        entity = map_to_save_rol_entity(params)
        db.add(entity)
        await db.flush()
        await db.refresh(entity)
        return map_to_rol(entity)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: RolUpdate) -> Union[Rol, None]:
        db = config.async_db
        stmt = select(RolEntity).filter(RolEntity.id == params.id)
        stmt.updated_date = datetime.now()
        result = await db.execute(stmt)
        rol = result.scalars().first()

        if not rol:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(rol, key, value)

        await db.flush()
        await db.refresh(rol)
        return map_to_rol(rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Rol], None]:
        db = config.async_db
        stmt = select(RolEntity)

        if params.filters:
            stmt = get_filter(
                query=stmt, filters=params.filters, entity=RolEntity
            )

        if not params.all_data:
            stmt = stmt.offset(params.skip).limit(params.limit)

        result = await db.execute(stmt)
        rols = result.scalars().all()

        if not rols:
            return None
        return map_to_list_rol(rols)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: RolDelete,
    ) -> Union[Rol, None]:
        db = config.async_db
        stmt = select(RolEntity).filter(RolEntity.id == params.id)
        result = await db.execute(stmt)
        rol = result.scalars().first()

        if not rol:
            return None

        await db.delete(rol)
        await db.flush()
        return map_to_rol(rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: RolRead,
    ) -> Union[Rol, None]:
        db = config.async_db
        stmt = select(RolEntity).filter(RolEntity.id == params.id)
        result = await db.execute(stmt)
        rol = result.scalars().first()

        if not rol:
            return None

        return map_to_rol(rol)
        