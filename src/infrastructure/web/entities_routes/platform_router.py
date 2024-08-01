from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.models.config import Config
from src.core.models.response import Response
from src.domain.models.entities.platform.platform_save import PlatformSave
from src.infrastructure.web.controller.entities.platform_controller import (
    PlatformController,
)


platform_router = APIRouter(
    prefix="/platform", tags=["Platform"], responses={404: {"description": "Not found"}}
)

platform_controller = PlatformController()


@platform_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
async def save(params: PlatformSave, config: Config = Depends(get_config)) -> Response:
    return platform_controller.save(config, params)
