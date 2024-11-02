
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
from src.domain.models.entities.user_location_rol.index import (
    UserLocationRol,
    UserLocationRolDelete,
    UserLocationRolRead,
    UserLocationRolUpdate,
)
from src.domain.services.repositories.entities.i_user_location_rol_repository import (
    IUserLocationRolRepository,
)
from src.infrastructure.database.entities.user_location_rol_entity import UserLocationRolEntity
from src.infrastructure.database.mappers.user_location_rol_mapper import (
    map_to_user_location_rol,
    map_to_list_user_location_rol,
)


class UserLocationRolRepository(IUserLocationRolRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: UserLocationRolEntity) -> Union[UserLocationRol, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_user_location_rol(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: UserLocationRolUpdate) -> Union[UserLocationRol, None]:
        async with config.async_db as db:
            stmt = select(UserLocationRolEntity).filter(UserLocationRolEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            user_location_rol = result.scalars().first()

            if not user_location_rol:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user_location_rol, key, value)

            await db.commit()
            await db.refresh(user_location_rol)
            return map_to_user_location_rol(user_location_rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[UserLocationRol], None]:
        async with config.async_db as db:
            stmt = select(UserLocationRolEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=UserLocationRolEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            user_location_rols = result.scalars().all()

            if not user_location_rols:
                return None
            return map_to_list_user_location_rol(user_location_rols)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: UserLocationRolDelete,
    ) -> Union[UserLocationRol, None]:
        async with config.async_db as db:
            stmt = select(UserLocationRolEntity).filter(UserLocationRolEntity.id == params.id)
            result = await db.execute(stmt)
            user_location_rol = result.scalars().first()

            if not user_location_rol:
                return None

            await db.delete(user_location_rol)
            await db.commit()
            return map_to_user_location_rol(user_location_rol)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: UserLocationRolRead,
    ) -> Union[UserLocationRol, None]:
        async with config.async_db as db:
            stmt = select(UserLocationRolEntity).filter(UserLocationRolEntity.id == params.id)
            result = await db.execute(stmt)
            user_location_rol = result.scalars().first()

            if not user_location_rol:
                return None

            return map_to_user_location_rol(user_location_rol)
        