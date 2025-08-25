from fastapi import APIRouter, Depends, status, Header
from typing import Optional
import httpx
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.methods.get_config import get_config, get_config_login
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.infrastructure.web.controller.mcps.mcp_controller import MCPController

# MCP Router for external API proxy
mcp_router = APIRouter(
    prefix="/mcp", 
    tags=["MCP"], 
    responses={404: {"description": "Not found"}},
    include_in_schema=True
)

mcp_controller = MCPController()

# Auth endpoints
@mcp_router.post(
    "/auth/login", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def auth_login(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    config: Config = Depends(get_config_login)
) -> dict:
    return await mcp_controller.auth_login(
        config=config, 
        request_data=request_data, 
        language=language
    )

@mcp_router.post(
    "/auth/refresh_token", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def auth_refresh_token(
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.auth_refresh_token(
        config=config, 
        language=language, 
        authorization=authorization
    )

@mcp_router.post(
    "/auth/logout", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def auth_logout(
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.auth_logout(
        config=config, 
        language=language, 
        authorization=authorization
    )

@mcp_router.post(
    "/auth/create-api-token", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def auth_create_api_token(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.auth_create_api_token(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

# API Token endpoints
@mcp_router.post(
    "/api-token", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def api_token_save(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.api_token_save(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

@mcp_router.put(
    "/api-token", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def api_token_update(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.api_token_update(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

@mcp_router.post(
    "/api-token/list", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def api_token_list(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.api_token_list(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

@mcp_router.delete(
    "/api-token/{id}", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def api_token_delete(
    id: str,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.api_token_delete(
        config=config, 
        id=id, 
        language=language, 
        authorization=authorization
    )

@mcp_router.get(
    "/api-token/{id}", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def api_token_read(
    id: str,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.api_token_read(
        config=config, 
        id=id, 
        language=language, 
        authorization=authorization
    )

# Currency Location endpoints
@mcp_router.post(
    "/currency-location", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def currency_location_save(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.currency_location_save(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

@mcp_router.put(
    "/currency-location", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def currency_location_update(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.currency_location_update(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

@mcp_router.post(
    "/currency-location/list", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def currency_location_list(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.currency_location_list(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

@mcp_router.delete(
    "/currency-location/{id}", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def currency_location_delete(
    id: str,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.currency_location_delete(
        config=config, 
        id=id, 
        language=language, 
        authorization=authorization
    )

@mcp_router.get(
    "/currency-location/{id}", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def currency_location_read(
    id: str,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.currency_location_read(
        config=config, 
        id=id, 
        language=language, 
        authorization=authorization
    )

# User endpoints
@mcp_router.post(
    "/user", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def user_save(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.user_save(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

@mcp_router.put(
    "/user", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def user_update(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.user_update(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

@mcp_router.post(
    "/user/list", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def user_list(
    request_data: dict,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.user_list(
        config=config, 
        request_data=request_data, 
        language=language, 
        authorization=authorization
    )

@mcp_router.delete(
    "/user/{id}", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def user_delete(
    id: str,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.user_delete(
        config=config, 
        id=id, 
        language=language, 
        authorization=authorization
    )

@mcp_router.get(
    "/user/{id}", 
    status_code=status.HTTP_200_OK, 
    response_model=dict
)
@execute_transaction_route(enabled=settings.has_track)
async def user_read(
    id: str,
    language: str = Header(..., description="Language header"),
    authorization: str = Header(..., description="Bearer token"),
    config: Config = Depends(get_config)
) -> dict:
    return await mcp_controller.user_read(
        config=config, 
        id=id, 
        language=language, 
        authorization=authorization
    )
