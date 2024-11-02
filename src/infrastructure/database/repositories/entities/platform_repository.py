
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.platform.index import (
    Platform,
    PlatformDelete,
    PlatformRead,
    PlatformUpdate,
)
from src.domain.services.repositories.entities.i_platform_repository import (
    IPlatformRepository,
)
from src.infrastructure.database.entities.platform_entity import PlatformEntity
from src.infrastructure.database.mappers.platform_mapper import (
    map_to_platform,
    map_to_list_platform,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class PlatformRepository(IPlatformRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: PlatformEntity) -> Union[Platform, None]:
        db: AsyncSession = config.async_db
        db.add(params)
        await db.commit()
        await db.refresh(params)
        return map_to_platform(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: PlatformUpdate) -> Union[Platform, None]:
        db: AsyncSession = config.async_db

        stmt = select(PlatformEntity).filter(PlatformEntity.id == params.id)
        result = await db.execute(stmt)
        platform = result.scalars().first()

        if not platform:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(platform, key, value)

        await db.commit()
        await db.refresh(platform)
        return map_to_platform(platform)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Platform], None]:
        db: AsyncSession = config.async_db
        stmt = select(PlatformEntity)

        if params.filters:
            stmt = get_filter(query=stmt, filters=params.filters, entity=PlatformEntity)

        if not params.all_data:
            stmt = stmt.offset(params.skip).limit(params.limit)

        result = await db.execute(stmt)
        platforms = result.scalars().all()

        if not platforms:
            return None
        return map_to_list_platform(platforms)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(self, config: Config, params: PlatformDelete) -> Union[Platform, None]:
        db: AsyncSession = config.async_db

        stmt = select(PlatformEntity).filter(PlatformEntity.id == params.id)
        result = await db.execute(stmt)
        platform = result.scalars().first()

        if not platform:
            return None

        await db.delete(platform)
        await db.commit()
        return map_to_platform(platform)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(self, config: Config, params: PlatformRead) -> Union[Platform, None]:
        async with config.async_db as db:
            stmt = select(PlatformEntity).filter(PlatformEntity.id == params.id)
            result = await db.execute(stmt)
            platform = result.scalars().first()

            if not platform:
                return None

            return map_to_platform(platform)
        