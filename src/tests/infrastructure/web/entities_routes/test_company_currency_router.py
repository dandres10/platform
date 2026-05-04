# SPEC-003 T8 / SPEC-001
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch
from contextlib import asynccontextmanager
from fastapi.testclient import TestClient

from src.core.models.config import Config
from src.core.models.access_token import AccessToken
from src.core.models.response import Response
from src.core.enums.permission_type import PERMISSION_TYPE
from src.tests._mock_utils import make_async_db_mock


def _config_factory(rol_code: str = "ADMIN", permissions: list = None):
    if permissions is None:
        permissions = [p.value for p in PERMISSION_TYPE]

    async def _get_config():
        cfg = Config()
        cfg.token = AccessToken(
            rol_id=str(uuid4()),
            rol_code=rol_code,
            user_id=str(uuid4()),
            location_id=str(uuid4()),
            currency_id=str(uuid4()),
            company_id=str(uuid4()),
            token_expiration_minutes=60,
            permissions=permissions,
        )
        cfg.async_db = make_async_db_mock()
        cfg.response_type = "object"
        cfg.language = "es"
        yield cfg
    return _get_config


@pytest.fixture
def app_with_admin():
    from main import app
    from src.core.methods.get_config import get_config
    app.dependency_overrides[get_config] = _config_factory("ADMIN")
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def app_with_user():
    from main import app
    from src.core.methods.get_config import get_config
    app.dependency_overrides[get_config] = _config_factory("USER")
    yield app
    app.dependency_overrides.clear()


def _ok_response():
    return Response.success(message="ok")


def test_save_happy_admin(app_with_admin):
    payload = {"company_id": str(uuid4()), "currency_id": str(uuid4()), "is_base": True}
    with patch(
        "src.infrastructure.web.entities_routes.company_currency_router.company_currency_controller.save",
        new=AsyncMock(return_value=_ok_response()),
    ):
        client = TestClient(app_with_admin)
        r = client.post("/company-currency", json=payload, headers={"Authorization": "Bearer x", "language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 200


def test_update_happy_admin(app_with_admin):
    payload = {"id": str(uuid4()), "is_base": True}
    with patch(
        "src.infrastructure.web.entities_routes.company_currency_router.company_currency_controller.update",
        new=AsyncMock(return_value=_ok_response()),
    ):
        client = TestClient(app_with_admin)
        r = client.put("/company-currency", json=payload, headers={"Authorization": "Bearer x", "language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 200


def test_list_happy_admin(app_with_admin):
    with patch(
        "src.infrastructure.web.entities_routes.company_currency_router.company_currency_controller.list",
        new=AsyncMock(return_value=_ok_response()),
    ):
        client = TestClient(app_with_admin)
        r = client.post("/company-currency/list", json={"all_data": True}, headers={"Authorization": "Bearer x", "language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 200


def test_delete_happy_admin(app_with_admin):
    with patch(
        "src.infrastructure.web.entities_routes.company_currency_router.company_currency_controller.delete",
        new=AsyncMock(return_value=_ok_response()),
    ):
        client = TestClient(app_with_admin)
        r = client.delete(f"/company-currency/{uuid4()}", headers={"Authorization": "Bearer x", "language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 200


def test_read_happy_admin(app_with_admin):
    with patch(
        "src.infrastructure.web.entities_routes.company_currency_router.company_currency_controller.read",
        new=AsyncMock(return_value=_ok_response()),
    ):
        client = TestClient(app_with_admin)
        r = client.get(f"/company-currency/{uuid4()}", headers={"Authorization": "Bearer x", "language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 200


def test_save_422_invalid_payload(app_with_admin):
    # company_id con valor no UUID → 422 (campo es Optional[UUID4])
    payload = {"company_id": "not-a-uuid", "currency_id": str(uuid4()), "is_base": True}
    client = TestClient(app_with_admin)
    r = client.post("/company-currency", json=payload, headers={"Authorization": "Bearer x", "language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 422


def test_save_403_user_role(app_with_user):
    # USER no puede save (solo ADMIN)
    payload = {"company_id": str(uuid4()), "currency_id": str(uuid4()), "is_base": True}
    client = TestClient(app_with_user)
    r = client.post("/company-currency", json=payload, headers={"Authorization": "Bearer x", "language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 403


def test_list_200_user_role(app_with_user):
    # USER SÍ puede list
    with patch(
        "src.infrastructure.web.entities_routes.company_currency_router.company_currency_controller.list",
        new=AsyncMock(return_value=_ok_response()),
    ):
        client = TestClient(app_with_user)
        r = client.post("/company-currency/list", json={"all_data": True}, headers={"Authorization": "Bearer x", "language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 200
