from fastapi import FastAPI

# imports
from src.infrastructure.web.entities_routes.api_token_router import api_token_router
from src.infrastructure.web.entities_routes.currency_location_router import currency_location_router
from src.infrastructure.web.entities_routes.currency_router import currency_router
from src.infrastructure.web.entities_routes.user_router import user_router
from src.infrastructure.web.entities_routes.translation_router import translation_router
from src.infrastructure.web.entities_routes.rol_router import rol_router
from src.infrastructure.web.entities_routes.language_router import language_router
from src.infrastructure.web.entities_routes.permission_router import permission_router
from src.infrastructure.web.entities_routes.menu_router import menu_router
from src.infrastructure.web.entities_routes.location_router import location_router
from src.infrastructure.web.entities_routes.user_location_rol_router import user_location_rol_router
from src.infrastructure.web.entities_routes.rol_permission_router import rol_permission_router
from src.infrastructure.web.entities_routes.platform_router import platform_router
from src.infrastructure.web.entities_routes.menu_permission_router import menu_permission_router
from src.infrastructure.web.entities_routes.company_router import company_router
from src.infrastructure.web.entities_routes.company_currency_router import company_currency_router
from src.infrastructure.web.entities_routes.geo_division_type_router import geo_division_type_router
from src.infrastructure.web.entities_routes.geo_division_router import geo_division_router
# SPEC-006 T7
from src.infrastructure.web.entities_routes.password_reset_token_router import (
    password_reset_token_router,
)



class Route:
    @staticmethod
    def set_routes(app: FastAPI):
        # include_router
        app.include_router(api_token_router)
        app.include_router(currency_location_router)
        app.include_router(currency_router)
        app.include_router(user_router)
        app.include_router(translation_router)
        app.include_router(rol_router)
        app.include_router(language_router)
        app.include_router(permission_router)
        app.include_router(menu_router)
        app.include_router(location_router)
        app.include_router(user_location_rol_router)
        app.include_router(rol_permission_router)
        app.include_router(platform_router)
        app.include_router(menu_permission_router)
        app.include_router(company_router)
        app.include_router(company_currency_router)
        app.include_router(geo_division_type_router)
        app.include_router(geo_division_router)
        # SPEC-006 T7
        app.include_router(password_reset_token_router)
        
