from fastapi import FastAPI
from src.core.config import settings
from src.infrastructure.web.routes.route import Route
from src.core.middleware.cors_app import CorsAppConfigurator
from src.core.middleware.redirect_to_docs import RedirectToDocsMiddleware

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
)

app.add_middleware(RedirectToDocsMiddleware)
CorsAppConfigurator.setup_cors(app)
Route.set_routes(app)
