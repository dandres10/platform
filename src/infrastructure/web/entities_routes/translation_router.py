from pydantic import UUID4
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.entities.translation.index import (
    TranslationDelete,
    TranslationRead,
    TranslationSave,
    TranslationUpdate,
)
from src.infrastructure.web.controller.entities.translation_controller import (
    TranslationController,
)


translation_router = APIRouter(
    prefix="/translation",
    tags=["Translation"],
    responses={404: {"description": "Not found"}},
)

translation_controller = TranslationController()


@translation_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def save(
    params: TranslationSave, config: Config = Depends(get_config)
) -> Response:
    return translation_controller.save(config=config, params=params)


@translation_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: TranslationUpdate, config: Config = Depends(get_config)
) -> Response:
    return translation_controller.update(config=config, params=params)


@translation_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return translation_controller.list(config=config, params=params)


@translation_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = TranslationDelete(id=id)
    return translation_controller.delete(config=config, params=build_params)


@translation_router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = TranslationRead(id=id)
    return translation_controller.read(config=config, params=build_params)
