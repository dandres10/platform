from typing import List, Union

from pydantic import UUID4
from sqlalchemy import inspect
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.language.language import Language
from src.domain.models.entities.language.language_delete import LanguageDelete
from src.domain.models.entities.language.language_read import LanguageRead
from src.domain.models.entities.language.language_update import LanguageUpdate
from src.domain.services.repositories.entities.i_language_repository import (
    ILanguageRepository,
)
from src.infrastructure.database.entities.language_entity import LanguageEntity
from src.infrastructure.database.mappers.language_mapper import (
    map_to_language,
    map_to_list_language,
)


class LanguageRepository(ILanguageRepository):

    def save(self, config: Config, params: LanguageEntity) -> Union[Language, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_language(params)

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


if settings.has_track:
    LanguageRepository.save = execute_transaction(LAYER.I_D_R.value)(
        LanguageRepository.save
    )
    LanguageRepository.update = execute_transaction(LAYER.I_D_R.value)(
        LanguageRepository.update
    )
    LanguageRepository.list = execute_transaction(LAYER.I_D_R.value)(
        LanguageRepository.list
    )
    LanguageRepository.delete = execute_transaction(LAYER.I_D_R.value)(
        LanguageRepository.delete
    )
    LanguageRepository.read = execute_transaction(LAYER.I_D_R.value)(
        LanguageRepository.read
    )
