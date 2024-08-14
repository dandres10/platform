from fastapi import FastAPI

# imports
from src.infrastructure.web.entities_routes.user_router import user_router
from src.infrastructure.web.entities_routes.translation_router import translation_router
from src.infrastructure.web.entities_routes.language_router import language_router
from src.infrastructure.web.business_routes.auth_router import auth_router


class Route:
    @staticmethod
    def set_routes(app: FastAPI):
        # include_router
        app.include_router(user_router)
        app.include_router(translation_router)
        app.include_router(language_router)
        app.include_router(auth_router)
