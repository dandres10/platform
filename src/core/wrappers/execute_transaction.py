import asyncio
import json
import logging
import traceback
from functools import wraps
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from src.core.exceptions import BusinessException


logger = logging.getLogger(__name__)


# SPEC-009 T1
_CONSTRAINT_TO_CODE: dict[str, str] = {}


def _translate_integrity_error(exc: Exception) -> tuple[int, dict]:
    """Traduce IntegrityError a respuesta segura sin filtrar SQL ni constraint names."""
    raw = str(getattr(exc, "orig", exc) or exc)
    for constraint_name, code in _CONSTRAINT_TO_CODE.items():
        if constraint_name in raw:
            return 409, {"code": code, "message": "constraint violation"}
    return 409, {"code": "CORE-CONFLICT", "message": "integrity constraint violation"}


def execute_transaction(layer, enabled=True):
    # SPEC-023: `enabled` controla solo logging y traducción de errores;
    # no afecta la transaccionalidad (cada repo gestiona su propia tx).
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not enabled:
                return await func(*args, **kwargs)
            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # SPEC-009 T1
                raise
            except Exception as e:
                class_name = func.__qualname__.split(".")[0]
                method_name = func.__name__

                params = kwargs.get("params", args[1] if len(args) > 1 else None)
                config = kwargs.get("config", args[0] if len(args) > 0 else None)

                params_data = {}
                if params:
                    try:
                        if hasattr(params, "dict"):
                            params_data = params.dict()
                        elif hasattr(params, "__dict__"):
                            params_data = params.__dict__
                        else:
                            params_data = str(params)
                    except Exception as ex:
                        params_data = f"Unserializable params: {ex}"

                config_data = {}
                if config:
                    try:
                        if hasattr(config, "dict"):
                            config_data = config.dict()
                        elif hasattr(config, "__dict__"):
                            config_data = {
                                k: (
                                    str(v)
                                    if not isinstance(
                                        v,
                                        (dict, list, str, int, float, bool, type(None)),
                                    )
                                    else v
                                )
                                for k, v in config.__dict__.items()
                            }
                        else:
                            config_data = str(config)
                    except Exception as ex:
                        config_data = f"Unserializable config: {ex}"

                tb = traceback.extract_tb(e.__traceback__)
                filename = tb[-1].filename
                line_number = tb[-1].lineno

                error_data = {
                    "layer": layer,
                    "class_name": class_name,
                    "method_name": method_name,
                    "params": params_data,
                    "config": config_data,
                    "error": str(e).replace("500:", "").lstrip(),
                    "file": filename,
                    "line": line_number,
                }

                error_json = json.dumps(error_data, indent=4, default=str)
                logger.error("TRANSACTION_ERROR: %s", error_json)

                # SPEC-009 T1
                if isinstance(e, BusinessException):
                    # SPEC-023
                    raise HTTPException(
                        status_code=409,
                        detail={"code": e.code or "CORE-INVALID", "key": e.key},
                    )
                if isinstance(e, IntegrityError):
                    status, detail = _translate_integrity_error(e)
                    raise HTTPException(status_code=status, detail=detail)
                if isinstance(e, ValueError):
                    raise HTTPException(
                        status_code=400,
                        detail={"code": "CORE-INVALID", "message": "invalid state or input"},
                    )
                raise HTTPException(
                    status_code=500,
                    detail={"code": "CORE-ERROR", "message": "internal error"},
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not enabled:
                return func(*args, **kwargs)
            try:
                return func(*args, **kwargs)
            except Exception:
                ...

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def string_to_json(text: str):
    try:
        cleaned_text = text.replace("\\n", "").replace("\\t", "").replace("\\", "")
        json_object = json.loads(cleaned_text)
        return json_object
    except json.JSONDecodeError:
        return None


def execute_transaction_route(enabled=True):
    # SPEC-023: `enabled` controla solo logging y traducción de errores;
    # no afecta la transaccionalidad. Body parsing ocurre antes del try
    # para evitar capturar errores de Pydantic dentro de logs de transacción.
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # SPEC-023
            config = kwargs.get("config", None)
            request = (
                config.request
                if config is not None and hasattr(config, "request")
                else None
            )

            if enabled and request is not None:
                body = await request.body()
                formatted_body = (
                    body.decode("utf-8") if isinstance(body, bytes) else str(body)
                )
                json_body = string_to_json(formatted_body)
                request.state.body = (
                    json_body if json_body is not None else formatted_body
                )

            if not enabled:
                return await func(*args, **kwargs)

            try:
                return await func(*args, **kwargs)
            except HTTPException:
                # SPEC-009 T1
                raise
            except Exception as e:
                route_info = {}

                if request and hasattr(request.state, "body"):
                    body_content = request.state.body

                    x_forwarded_for = request.headers.get("X-Forwarded-For")
                    if x_forwarded_for:
                        client_ip = x_forwarded_for.split(",")[0]
                    else:
                        client_ip = request.client.host

                    route_info = {
                        "method": request.method,
                        "url": str(request.url),
                        "path": request.url.path,
                        "query_params": dict(request.query_params),
                        "headers": dict(request.headers),
                        "ip": client_ip,
                    }

                    if isinstance(body_content, dict):
                        route_info["json_body"] = body_content
                    else:
                        route_info["body"] = body_content
                else:
                    route_info = {
                        "method": "unknown",
                        "url": "unknown",
                        "path": "unknown",
                        "query_params": {},
                        "headers": {},
                        "body": "No request data available",
                    }

                error_info = {
                    "error": f"{e}".replace("500:", "").lstrip(),
                    "route_info": route_info,
                }

                logger.error("ROUTE_ERROR: %s", json.dumps(error_info, indent=4, default=str))

                # SPEC-009 T1
                if isinstance(e, BusinessException):
                    # SPEC-023
                    raise HTTPException(
                        status_code=409,
                        detail={"code": e.code or "CORE-INVALID", "key": e.key},
                    )
                if isinstance(e, IntegrityError):
                    status, detail = _translate_integrity_error(e)
                    raise HTTPException(status_code=status, detail=detail)
                if isinstance(e, ValueError):
                    raise HTTPException(
                        status_code=400,
                        detail={"code": "CORE-INVALID", "message": "invalid state or input"},
                    )
                raise HTTPException(
                    status_code=500,
                    detail={"code": "CORE-ERROR", "message": "internal error"},
                )

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not enabled:
                return func(*args, **kwargs)
            try:
                return func(*args, **kwargs)
            except Exception:
                ...

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator
