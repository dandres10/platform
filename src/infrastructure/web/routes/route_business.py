from fastapi import APIRouter, FastAPI

from src.infrastructure.web.business_routes.auth_router import auth_router
from src.infrastructure.web.business_routes.geography_router import geography_router
from src.infrastructure.web.business_routes.catalog_router import catalog_router

v1_router = APIRouter(prefix="/v1")


class RouteBusiness:
    @staticmethod
    def set_routes(app: FastAPI):
        v1_router.include_router(auth_router)
        v1_router.include_router(geography_router)
        v1_router.include_router(catalog_router)
        app.include_router(v1_router)
