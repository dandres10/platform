
from typing import List
from src.domain.models.entities.translation.index import (
    Translation,
    TranslationSave,
    TranslationUpdate,
)
from src.infrastructure.database.entities.translation_entity import TranslationEntity


def map_to_translation(translation_entity: TranslationEntity) -> Translation:
    return Translation(
        id=translation_entity.id,
        key=translation_entity.key,
        language_code=translation_entity.language_code,
        translation=translation_entity.translation,
        context=translation_entity.context,
        state=translation_entity.state,
        created_date=translation_entity.created_date,
        updated_date=translation_entity.updated_date,
    )

def map_to_list_translation(translation_entities: List[TranslationEntity]) -> List[Translation]:
    return [map_to_translation(translation) for translation in translation_entities]

def map_to_translation_entity(translation: Translation) -> TranslationEntity:
    return TranslationEntity(
        id=translation.id,
        key=translation.key,
        language_code=translation.language_code,
        translation=translation.translation,
        context=translation.context,
        state=translation.state,
        created_date=translation.created_date,
        updated_date=translation.updated_date,
    )

def map_to_list_translation_entity(translations: List[Translation]) -> List[TranslationEntity]:
    return [map_to_translation_entity(translation) for translation in translations]

def map_to_save_translation_entity(translation: TranslationSave) -> TranslationEntity:
    return TranslationEntity(
        key=translation.key,
        language_code=translation.language_code,
        translation=translation.translation,
        context=translation.context,
        state=translation.state,
    )

def map_to_update_translation_entity(translation: TranslationUpdate) -> TranslationEntity:
    return TranslationEntity(
        id=translation.id,
        key=translation.key,
        language_code=translation.language_code,
        translation=translation.translation,
        context=translation.context,
        state=translation.state,
    )

