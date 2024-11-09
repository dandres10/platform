
from typing import List
from src.domain.models.entities.api_token.index import (
    ApiToken,
    ApiTokenSave,
    ApiTokenUpdate,
)
from src.infrastructure.database.entities.api_token_entity import ApiTokenEntity


def map_to_api_token(api_token_entity: ApiTokenEntity) -> ApiToken:
    return ApiToken(
        id=api_token_entity.id,
        rol_id=api_token_entity.rol_id,
        token=api_token_entity.token,
        state=api_token_entity.state,
        created_date=api_token_entity.created_date,
        updated_date=api_token_entity.updated_date,
    )

def map_to_list_api_token(api_token_entities: List[ApiTokenEntity]) -> List[ApiToken]:
    return [map_to_api_token(api_token) for api_token in api_token_entities]

def map_to_api_token_entity(api_token: ApiToken) -> ApiTokenEntity:
    return ApiTokenEntity(
        id=api_token.id,
        rol_id=api_token.rol_id,
        token=api_token.token,
        state=api_token.state,
        created_date=api_token.created_date,
        updated_date=api_token.updated_date,
    )

def map_to_list_api_token_entity(api_tokens: List[ApiToken]) -> List[ApiTokenEntity]:
    return [map_to_api_token_entity(api_token) for api_token in api_tokens]

def map_to_save_api_token_entity(api_token: ApiTokenSave) -> ApiTokenEntity:
    return ApiTokenEntity(
        rol_id=api_token.rol_id,
        token=api_token.token,
        state=api_token.state,
    )

def map_to_update_api_token_entity(api_token: ApiTokenUpdate) -> ApiTokenEntity:
    return ApiTokenEntity(
        id=api_token.id,
        rol_id=api_token.rol_id,
        token=api_token.token,
        state=api_token.state,
    )

