from fastapi import FastAPI

# imports
from src.infrastructure.web.business_routes.auth_router import auth_router


class Route:
    @staticmethod
    def set_routes(app: FastAPI):
        # include_router
        app.include_router(auth_router)
