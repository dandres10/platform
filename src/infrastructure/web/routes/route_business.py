from fastapi import FastAPI

# imports
from src.infrastructure.web.business_routes.auth_router import auth_router
from src.infrastructure.web.business_routes.geography_router import geography_router
from src.infrastructure.web.business_routes.catalog_router import catalog_router



class RouteBusiness:
    @staticmethod
    def set_routes(app: FastAPI):
        # include_router
        app.include_router(auth_router)
        app.include_router(geography_router)
        app.include_router(catalog_router)
