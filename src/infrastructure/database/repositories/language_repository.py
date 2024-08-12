
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
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
    def save(self, config: Config, params: LanguageEntity) -> Union[Language, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_language(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: LanguageUpdate) -> Union[Language, None]:
        db = config.db

        language: LanguageEntity = (
            db.query(LanguageEntity).filter(LanguageEntity.id == params.id).first()
        )

        if not language:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(language, key, value)

        db.commit()
        db.refresh(language)
        return map_to_language(language)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Language], None]:
        db = config.db
        query = db.query(LanguageEntity)

        if params.all_data:
            languages = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=LanguageEntity
                )
                languages = query.offset(params.skip).limit(params.limit).all()

        if not languages:
            return None
        return map_to_list_language(languages)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: LanguageDelete,
    ) -> Union[Language, None]:
        db = config.db
        language: LanguageEntity = (
            db.query(LanguageEntity).filter(LanguageEntity.id == params.id).first()
        )

        if not language:
            return None

        db.delete(language)
        db.commit()
        return map_to_language(language)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: LanguageRead,
    ) -> Union[Language, None]:
        db = config.db
        language: LanguageEntity = (
            db.query(LanguageEntity).filter(LanguageEntity.id == params.id).first()
        )

        if not language:
            return None

        return map_to_language(language)
        