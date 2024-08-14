
from pydantic import UUID4
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.entities.company.index import (
    CompanyDelete,
    CompanyRead,
    CompanySave,
    CompanyUpdate,
)
from src.infrastructure.web.controller.entities.company_controller import (
    CompanyController,
)


company_router = APIRouter(
    prefix="/company", tags=["Company"], responses={404: {"description": "Not found"}}
)

company_controller = CompanyController()


@company_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def save(params: CompanySave, config: Config = Depends(get_config)) -> Response:
    return company_controller.save(config=config, params=params)


@company_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: CompanyUpdate, config: Config = Depends(get_config)
) -> Response:
    return company_controller.update(config=config, params=params)


@company_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return company_controller.list(config=config, params=params)


@company_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = CompanyDelete(id=id)
    return company_controller.delete(config=config, params=build_params)


@company_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = CompanyRead(id=id)
    return company_controller.read(config=config, params=build_params)

    