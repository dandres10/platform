
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
from src.domain.models.entities.api_token.index import (
    ApiToken,
    ApiTokenDelete,
    ApiTokenRead,
    ApiTokenUpdate,
)
from src.domain.services.repositories.entities.i_api_token_repository import (
    IApiTokenRepository,
)
from src.infrastructure.database.entities.api_token_entity import ApiTokenEntity
from src.infrastructure.database.mappers.api_token_mapper import (
    map_to_api_token,
    map_to_list_api_token,
)


class ApiTokenRepository(IApiTokenRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: ApiTokenEntity) -> Union[ApiToken, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_api_token(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: ApiTokenUpdate) -> Union[ApiToken, None]:
        async with config.async_db as db:
            stmt = select(ApiTokenEntity).filter(ApiTokenEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            api_token = result.scalars().first()

            if not api_token:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(api_token, key, value)

            await db.commit()
            await db.refresh(api_token)
            return map_to_api_token(api_token)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[ApiToken], None]:
        async with config.async_db as db:
            stmt = select(ApiTokenEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=ApiTokenEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            api_tokens = result.scalars().all()

            if not api_tokens:
                return None
            return map_to_list_api_token(api_tokens)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: ApiTokenDelete,
    ) -> Union[ApiToken, None]:
        async with config.async_db as db:
            stmt = select(ApiTokenEntity).filter(ApiTokenEntity.id == params.id)
            result = await db.execute(stmt)
            api_token = result.scalars().first()

            if not api_token:
                return None

            await db.delete(api_token)
            await db.commit()
            return map_to_api_token(api_token)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: ApiTokenRead,
    ) -> Union[ApiToken, None]:
        async with config.async_db as db:
            stmt = select(ApiTokenEntity).filter(ApiTokenEntity.id == params.id)
            result = await db.execute(stmt)
            api_token = result.scalars().first()

            if not api_token:
                return None

            return map_to_api_token(api_token)
        