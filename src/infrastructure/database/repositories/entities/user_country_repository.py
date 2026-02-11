
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
from src.domain.models.entities.user_country.index import (
    UserCountry,
    UserCountryDelete,
    UserCountryRead,
    UserCountryUpdate,
)
from src.domain.services.repositories.entities.i_user_country_repository import (
    IUserCountryRepository,
)
from src.infrastructure.database.entities.user_country_entity import UserCountryEntity
from src.infrastructure.database.mappers.user_country_mapper import (
    map_to_user_country,
    map_to_list_user_country,
)


class UserCountryRepository(IUserCountryRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: UserCountryEntity) -> Union[UserCountry, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_user_country(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: UserCountryUpdate) -> Union[UserCountry, None]:
        async with config.async_db as db:
            stmt = select(UserCountryEntity).filter(UserCountryEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            user_country = result.scalars().first()

            if not user_country:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user_country, key, value)

            await db.commit()
            await db.refresh(user_country)
            return map_to_user_country(user_country)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[UserCountry], None]:
        async with config.async_db as db:
            stmt = select(UserCountryEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=UserCountryEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            user_countries = result.scalars().all()

            if not user_countries:
                return None
            return map_to_list_user_country(user_countries)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: UserCountryDelete,
    ) -> Union[UserCountry, None]:
        async with config.async_db as db:
            stmt = select(UserCountryEntity).filter(UserCountryEntity.id == params.id)
            result = await db.execute(stmt)
            user_country = result.scalars().first()

            if not user_country:
                return None

            await db.delete(user_country)
            await db.commit()
            return map_to_user_country(user_country)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: UserCountryRead,
    ) -> Union[UserCountry, None]:
        async with config.async_db as db:
            stmt = select(UserCountryEntity).filter(UserCountryEntity.id == params.id)
            result = await db.execute(stmt)
            user_country = result.scalars().first()

            if not user_country:
                return None

            return map_to_user_country(user_country)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read_by_user_id(
        self,
        config: Config,
        user_id: UUID4,
    ) -> Union[UserCountry, None]:
        """Obtiene el país de un usuario por su user_id"""
        async with config.async_db as db:
            stmt = select(UserCountryEntity).filter(UserCountryEntity.user_id == user_id)
            result = await db.execute(stmt)
            user_country = result.scalars().first()

            if not user_country:
                return None

            return map_to_user_country(user_country)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete_by_user_id(
        self,
        config: Config,
        user_id: UUID4,
    ) -> Union[UserCountry, None]:
        """Elimina el registro de país de un usuario por su user_id"""
        async with config.async_db as db:
            stmt = select(UserCountryEntity).filter(UserCountryEntity.user_id == user_id)
            result = await db.execute(stmt)
            user_country = result.scalars().first()

            if not user_country:
                return None

            await db.delete(user_country)
            await db.commit()
            return map_to_user_country(user_country)
