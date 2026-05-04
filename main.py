from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.config import settings
from src.core.middleware.user_rate_limit_middleware import UserRateLimitMiddleware
from src.infrastructure.web.routes.route import Route
from src.infrastructure.web.routes.route_business import RouteBusiness
from src.core.middleware.cors_app import CorsAppConfigurator
from src.core.middleware.redirect_to_docs import RedirectToDocsMiddleware
from src.infrastructure.web.routes.route_mcp import RouteMcp, mcp_business
from src.infrastructure.web.health_router import health_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with mcp_business.session_manager.run():
        yield


app = FastAPI(
    title=settings.project_name,
    description=f"{settings.project_description} [{settings.app_environment}]",
    version=settings.project_version,
    lifespan=lifespan,
)

# SPEC-020
# SPEC-029 T3
if settings.rate_limit_enabled:
    app.add_middleware(UserRateLimitMiddleware)

app.add_middleware(RedirectToDocsMiddleware)
CorsAppConfigurator.setup_cors(app)
# SPEC-021
app.include_router(health_router)
RouteBusiness.set_routes(app)
Route.set_routes(app)
RouteMcp.set_routes(app)
