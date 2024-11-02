from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status, WebSocket
from src.core.config import settings
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.wrappers.check_permissions import check_permissions
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.infrastructure.database.entities.currency_entity import CurrencyEntity
from src.infrastructure.web.controller.business.auth_controller import AuthController
from src.core.methods.get_config import get_config, get_config_login


auth_router = APIRouter(
    prefix="/auth", tags=["Auth"], responses={404: {"description": "Not found"}}
)

auth_controller = AuthController()


@auth_router.post("/login", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def login(
    params: AuthLoginRequest, config: Config = Depends(get_config_login)
) -> Response:
    return await auth_controller.login(config=config, params=params)


@auth_router.post(
    "/refresh_token", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def refresh_token(config: Config = Depends(get_config)) -> Response:
    return await auth_controller.refresh_token(config=config)


@auth_router.post("/logout", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def logout(config: Config = Depends(get_config)) -> Response:
    return await auth_controller.logout(config=config)


@auth_router.post("/obtener_servicios", response_model=List[dict])
async def obtener_servicios(token: str = Query(...)):

    if token != "ead47080-0d60-45da-98b7-57c9a302b662":
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "message": "Token is invalid or expired"},
        )

    servicios = [
        {
            "nombre": "Limpieza Dental",
            "descripcion": "Limpieza profesional de los dientes",
            "precio": 15000,
        },
        {
            "nombre": "Ortodoncia",
            "descripcion": "Alineación de los dientes con brackets",
            "precio": 500000,
        },
        {
            "nombre": "Blanqueamiento Dental",
            "descripcion": "Blanqueamiento para mejorar la estética",
            "precio": 300000,
        },
        {
            "nombre": "Extracción Dental",
            "descripcion": "Extracción de muelas o dientes",
            "precio": 200000,
        },
        {
            "nombre": "Implante Dental",
            "descripcion": "Reemplazo de un diente perdido con un implante",
            "precio": 4500000,
        },
    ]
    return servicios


@auth_router.post("/validar_disponibilidad", response_model=str)
async def validar_disponibilidad(token: str = Query(...)):
    # Verificar el token (aquí puedes agregar tu lógica para validar el token si es necesario)

    if token != "ead47080-0d60-45da-98b7-57c9a302b662":
        raise HTTPException(
            status_code=401,
            detail={"error": "Unauthorized", "message": "Token is invalid or expired"},
        )

    # Lógica de disponibilidad del calendario
    has_space_calendar = False

    if not has_space_calendar:
        return "No tenemos disponibilidad."

    return "Sí tenemos disponibilidad."



