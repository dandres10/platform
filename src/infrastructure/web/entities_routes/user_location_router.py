
from pydantic import UUID4
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.entities.user_location.index import (
    UserLocationDelete,
    UserLocationRead,
    UserLocationSave,
    UserLocationUpdate,
)
from src.infrastructure.web.controller.entities.user_location_controller import (
    UserLocationController,
)


user_location_router = APIRouter(
    prefix="/user-location", tags=["UserLocation"], responses={404: {"description": "Not found"}}
)

user_location_controller = UserLocationController()


@user_location_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def save(params: UserLocationSave, config: Config = Depends(get_config)) -> Response:
    return user_location_controller.save(config=config, params=params)


@user_location_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: UserLocationUpdate, config: Config = Depends(get_config)
) -> Response:
    return user_location_controller.update(config=config, params=params)


@user_location_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return user_location_controller.list(config=config, params=params)


@user_location_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = UserLocationDelete(id=id)
    return user_location_controller.delete(config=config, params=build_params)


@user_location_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = UserLocationRead(id=id)
    return user_location_controller.read(config=config, params=build_params)

    