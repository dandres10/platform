# SPEC-006 T3
from fastapi import APIRouter, Depends, status

from src.core.config import settings
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.methods.get_config import get_config
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.wrappers.check_permissions import check_permissions
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.business.notifications.send_email_request import (
    SendEmailRequest,
)
from src.infrastructure.web.controller.business.notifications_controller import (
    NotificationsController,
)


notifications_router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
    responses={404: {"description": "Not found"}},
)

notifications_controller = NotificationsController()


@notifications_router.post(
    "/email",
    status_code=status.HTTP_200_OK,
    response_model=Response[bool],
)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def send_email(
    params: SendEmailRequest, config: Config = Depends(get_config)
) -> Response[bool]:
    return await notifications_controller.send_email(config=config, params=params)
