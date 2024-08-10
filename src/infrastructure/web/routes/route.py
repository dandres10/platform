from fastapi import FastAPI

# imports
from src.infrastructure.web.entities_routes.translation_router import translation_router
from src.infrastructure.web.entities_routes.currency_router import currency_router
from src.infrastructure.web.entities_routes.platform_router import platform_router
from src.infrastructure.web.entities_routes.language_router import language_router


class Route:
    @staticmethod
    def set_routes(app: FastAPI):
        # include_router
        app.include_router(translation_router)
        app.include_router(platform_router)
        app.include_router(language_router)
        app.include_router(currency_router)
