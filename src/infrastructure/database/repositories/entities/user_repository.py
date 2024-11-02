
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
from src.domain.models.entities.user.index import (
    User,
    UserDelete,
    UserRead,
    UserUpdate,
)
from src.domain.services.repositories.entities.i_user_repository import (
    IUserRepository,
)
from src.infrastructure.database.entities.user_entity import UserEntity
from src.infrastructure.database.mappers.user_mapper import (
    map_to_user,
    map_to_list_user,
)


class UserRepository(IUserRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: UserEntity) -> Union[User, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_user(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: UserUpdate) -> Union[User, None]:
        async with config.async_db as db:
            stmt = select(UserEntity).filter(UserEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user, key, value)

            await db.commit()
            await db.refresh(user)
            return map_to_user(user)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[User], None]:
        async with config.async_db as db:
            stmt = select(UserEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=UserEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            users = result.scalars().all()

            if not users:
                return None
            return map_to_list_user(users)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: UserDelete,
    ) -> Union[User, None]:
        async with config.async_db as db:
            stmt = select(UserEntity).filter(UserEntity.id == params.id)
            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                return None

            await db.delete(user)
            await db.commit()
            return map_to_user(user)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: UserRead,
    ) -> Union[User, None]:
        async with config.async_db as db:
            stmt = select(UserEntity).filter(UserEntity.id == params.id)
            result = await db.execute(stmt)
            user = result.scalars().first()

            if not user:
                return None

            return map_to_user(user)
        