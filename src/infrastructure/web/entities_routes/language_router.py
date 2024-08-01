from pydantic import UUID4
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.domain.models.entities.language.language_delete import LanguageDelete
from src.domain.models.entities.language.language_read import LanguageRead
from src.domain.models.entities.language.language_save import LanguageSave
from src.domain.models.entities.language.language_update import LanguageUpdate
from src.infrastructure.web.controller.entities.language_controller import (
    LanguageController,
)


language_router = APIRouter(
    prefix="/language", tags=["Language"], responses={404: {"description": "Not found"}}
)

language_controller = LanguageController()


@language_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
async def save(params: LanguageSave, config: Config = Depends(get_config)) -> Response:
    return language_controller.save(config, params)


@language_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
async def update(
    params: LanguageUpdate, config: Config = Depends(get_config)
) -> Response:
    return language_controller.update(config, params)


@language_router.post(
    "/languages", status_code=status.HTTP_200_OK, response_model=Response
)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return language_controller.list(config, params)


@language_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = LanguageDelete(id=id)
    return language_controller.delete(config, params=build_params)


@language_router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = LanguageRead(id=id)
    return language_controller.read(config, params=build_params)
