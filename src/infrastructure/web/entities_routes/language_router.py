
from pydantic import UUID4
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.entities.language.index import (
    LanguageDelete,
    LanguageRead,
    LanguageSave,
    LanguageUpdate,
)
from src.infrastructure.web.controller.entities.language_controller import (
    LanguageController,
)


language_router = APIRouter(
    prefix="/language", tags=["Language"], responses={404: {"description": "Not found"}}
)

language_controller = LanguageController()


@language_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def save(params: LanguageSave, config: Config = Depends(get_config)) -> Response:
    return language_controller.save(config=config, params=params)


@language_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: LanguageUpdate, config: Config = Depends(get_config)
) -> Response:
    return language_controller.update(config=config, params=params)


@language_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return language_controller.list(config=config, params=params)


@language_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = LanguageDelete(id=id)
    return language_controller.delete(config=config, params=build_params)


@language_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = LanguageRead(id=id)
    return language_controller.read(config=config, params=build_params)

    