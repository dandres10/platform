
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
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
    def save(self, config: Config, params: TranslationEntity) -> Union[Translation, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_translation(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: TranslationUpdate) -> Union[Translation, None]:
        db = config.db

        translation: TranslationEntity = (
            db.query(TranslationEntity).filter(TranslationEntity.id == params.id).first()
        )

        if not translation:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(translation, key, value)

        db.commit()
        db.refresh(translation)
        return map_to_translation(translation)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Translation], None]:
        db = config.db
        query = db.query(TranslationEntity)

        if params.all_data:
            translations = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=TranslationEntity
                )
                translations = query.offset(params.skip).limit(params.limit).all()

        if not translations:
            return None
        return map_to_list_translation(translations)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: TranslationDelete,
    ) -> Union[Translation, None]:
        db = config.db
        translation: TranslationEntity = (
            db.query(TranslationEntity).filter(TranslationEntity.id == params.id).first()
        )

        if not translation:
            return None

        db.delete(translation)
        db.commit()
        return map_to_translation(translation)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: TranslationRead,
    ) -> Union[Translation, None]:
        db = config.db
        translation: TranslationEntity = (
            db.query(TranslationEntity).filter(TranslationEntity.id == params.id).first()
        )

        if not translation:
            return None

        return map_to_translation(translation)
        