# SPEC-028 T4
import json
import logging
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from src.core.wrappers.execute_transaction import (
    execute_transaction,
    execute_transaction_route,
)


PASSWORD_PLAIN = "super_secret_pwd_42"
JWT_PLAIN = "Bearer eyJsecretTokenValue"


class _FakeURL(str):
    def __new__(cls, path: str):
        instance = super().__new__(cls, f"http://test{path}")
        instance.path = path
        return instance


class _FakeRequest:
    def __init__(self, json_body: dict, headers: dict, query_params: dict):
        self._body_bytes = json.dumps(json_body).encode("utf-8")
        self.headers = headers
        self.query_params = query_params
        self.method = "POST"
        self.url = _FakeURL("/v1/auth/login")
        self.client = SimpleNamespace(host="127.0.0.1")
        self.state = SimpleNamespace()

    async def body(self):
        return self._body_bytes


def _config_with_request():
    request = _FakeRequest(
        json_body={"email": "a@b.com", "password": PASSWORD_PLAIN},
        headers={"Authorization": JWT_PLAIN, "Content-Type": "application/json"},
        query_params={},
    )
    cfg = SimpleNamespace(request=request, async_db=None)
    return cfg


async def test_route_error_log_redacts_password_and_authorization(caplog):
    @execute_transaction_route(enabled=True)
    async def fake_route(config):
        raise RuntimeError("boom inside route")

    cfg = _config_with_request()
    caplog.set_level(logging.ERROR, logger="src.core.wrappers.execute_transaction")

    with pytest.raises(HTTPException):
        await fake_route(config=cfg)

    log_text = caplog.text
    assert "ROUTE_ERROR" in log_text
    assert PASSWORD_PLAIN not in log_text
    assert JWT_PLAIN not in log_text
    assert "<redacted>" in log_text
    assert "a@b.com" in log_text


async def test_transaction_error_log_redacts_sensitive_params():
    @execute_transaction("business", enabled=True)
    async def fake_uc(config, params):
        raise RuntimeError("boom inside uc")

    sensitive_params = SimpleNamespace(
        email="a@b.com",
        password=PASSWORD_PLAIN,
    )
    sensitive_params.dict = lambda: {"email": "a@b.com", "password": PASSWORD_PLAIN}

    cfg = SimpleNamespace(jwt_secret_key="mysecretkey", language="es")
    cfg.dict = lambda: {"jwt_secret_key": "mysecretkey", "language": "es"}

    import logging as _logging
    handler_records = []

    class _Capture(_logging.Handler):
        def emit(self, record):
            handler_records.append(self.format(record))

    capture = _Capture(level=_logging.ERROR)
    capture.setFormatter(_logging.Formatter("%(message)s"))
    logger = _logging.getLogger("src.core.wrappers.execute_transaction")
    logger.addHandler(capture)
    logger.setLevel(_logging.ERROR)
    try:
        with pytest.raises(HTTPException):
            await fake_uc(cfg, sensitive_params)
    finally:
        logger.removeHandler(capture)

    log_text = "\n".join(handler_records)
    assert "TRANSACTION_ERROR" in log_text
    assert PASSWORD_PLAIN not in log_text
    assert "mysecretkey" not in log_text
    assert "<redacted>" in log_text
    assert "a@b.com" in log_text
