
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
from src.domain.models.entities.language.index import (
    Language,
    LanguageDelete,
    LanguageRead,
    LanguageUpdate,
)
from src.domain.services.repositories.entities.i_language_repository import (
    ILanguageRepository,
)
from src.infrastructure.database.entities.language_entity import LanguageEntity
from src.infrastructure.database.mappers.language_mapper import (
    map_to_language,
    map_to_list_language,
)


class LanguageRepository(ILanguageRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: LanguageEntity) -> Union[Language, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_language(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: LanguageUpdate) -> Union[Language, None]:
        async with config.async_db as db:
            stmt = select(LanguageEntity).filter(LanguageEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            language = result.scalars().first()

            if not language:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(language, key, value)

            await db.commit()
            await db.refresh(language)
            return map_to_language(language)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Language], None]:
        async with config.async_db as db:
            stmt = select(LanguageEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=LanguageEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            languages = result.scalars().all()

            if not languages:
                return None
            return map_to_list_language(languages)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: LanguageDelete,
    ) -> Union[Language, None]:
        async with config.async_db as db:
            stmt = select(LanguageEntity).filter(LanguageEntity.id == params.id)
            result = await db.execute(stmt)
            language = result.scalars().first()

            if not language:
                return None

            await db.delete(language)
            await db.commit()
            return map_to_language(language)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: LanguageRead,
    ) -> Union[Language, None]:
        async with config.async_db as db:
            stmt = select(LanguageEntity).filter(LanguageEntity.id == params.id)
            result = await db.execute(stmt)
            language = result.scalars().first()

            if not language:
                return None

            return map_to_language(language)
        