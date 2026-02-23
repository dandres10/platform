from typing import List
from fastapi import APIRouter, Depends, status
from src.core.config import settings
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.enums.rol_type import ROL_TYPE
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.models.filter import Pagination
from src.core.wrappers.check_permissions import check_permissions
from src.core.wrappers.check_roles import check_roles
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.core.methods.get_config import get_config
from src.domain.models.business.catalog.list_companies import CompanyItem
from src.domain.models.business.catalog.list_locations_by_company import LocationItem
from src.infrastructure.web.controller.business.catalog_controller import (
    CatalogController,
)


catalog_router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"],
    responses={404: {"description": "Not found"}},
)

catalog_controller = CatalogController()


@catalog_router.post(
    "/companies",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[CompanyItem]],
)
@check_permissions([PERMISSION_TYPE.LIST.value])
@check_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@execute_transaction_route(enabled=settings.has_track)
async def list_companies(
    params: Pagination, config: Config = Depends(get_config)
) -> Response[List[CompanyItem]]:
    return await catalog_controller.list_companies(config=config, params=params)


@catalog_router.post(
    "/locations",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[LocationItem]],
)
@check_permissions([PERMISSION_TYPE.LIST.value])
@check_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@execute_transaction_route(enabled=settings.has_track)
async def list_locations_by_company(
    params: Pagination, config: Config = Depends(get_config)
) -> Response[List[LocationItem]]:
    return await catalog_controller.list_locations_by_company(
        config=config, params=params
    )
