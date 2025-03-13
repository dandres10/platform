
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
from src.domain.models.entities.translation.index import (
    Translation,
    TranslationDelete,
    TranslationRead,
    TranslationUpdate,
)
from src.domain.services.repositories.entities.i_translation_repository import (
    ITranslationRepository,
)
from src.infrastructure.database.entities.translation_entity import TranslationEntity
from src.infrastructure.database.mappers.translation_mapper import (
    map_to_translation,
    map_to_list_translation,
)


class TranslationRepository(ITranslationRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: TranslationEntity) -> Union[Translation, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_translation(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: TranslationUpdate) -> Union[Translation, None]:
        async with config.async_db as db:
            stmt = select(TranslationEntity).filter(TranslationEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            translation = result.scalars().first()

            if not translation:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(translation, key, value)

            await db.commit()
            await db.refresh(translation)
            return map_to_translation(translation)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Translation], None]:
        async with config.async_db as db:
            stmt = select(TranslationEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=TranslationEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            translations = result.scalars().all()

            if not translations:
                return None
            return map_to_list_translation(translations)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: TranslationDelete,
    ) -> Union[Translation, None]:
        async with config.async_db as db:
            stmt = select(TranslationEntity).filter(TranslationEntity.id == params.id)
            result = await db.execute(stmt)
            translation = result.scalars().first()

            if not translation:
                return None

            await db.delete(translation)
            await db.commit()
            return map_to_translation(translation)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: TranslationRead,
    ) -> Union[Translation, None]:
        async with config.async_db as db:
            stmt = select(TranslationEntity).filter(TranslationEntity.id == params.id)
            result = await db.execute(stmt)
            translation = result.scalars().first()

            if not translation:
                return None

            return map_to_translation(translation)
        