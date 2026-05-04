# SPEC-006 T3
import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from src.core.models.access_token import AccessToken
from src.core.models.config import Config
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
def app_no_save_permission():
    from main import app
    from src.core.methods.get_config import get_config
    perms = [p.value for p in PERMISSION_TYPE if p.value != PERMISSION_TYPE.SAVE.value]
    app.dependency_overrides[get_config] = _config_factory("USER", perms)
    yield app
    app.dependency_overrides.clear()


def _ok_response():
    return Response.success_temporary_message(response=True, message="ok")


def test_send_email_happy_path(app_with_admin):
    payload = {
        "to": "alice@test.com",
        "subject_key": "email_welcome_subject",
        "body_key": "email_welcome_body",
        "template_vars": {"name": "Alice"},
    }
    with patch(
        "src.infrastructure.web.business_routes.notifications_router.notifications_controller.send_email",
        new=AsyncMock(return_value=_ok_response()),
    ):
        client = TestClient(app_with_admin)
        r = client.post(
            "/v1/notifications/email",
            json=payload,
            headers={
                "Authorization": "Bearer x",
                "language": "es",
                "timezone": "America/Bogota",
            },
        )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"
    assert body["response"] is True


def test_send_email_validates_required_fields(app_with_admin):
    payload = {"to": "alice@test.com"}
    client = TestClient(app_with_admin)
    r = client.post(
        "/v1/notifications/email",
        json=payload,
        headers={
            "Authorization": "Bearer x",
            "language": "es",
            "timezone": "America/Bogota",
        },
    )
    assert r.status_code == 422


def test_send_email_rejected_without_save_permission(app_no_save_permission):
    payload = {
        "to": "alice@test.com",
        "subject_key": "email_welcome_subject",
        "body_key": "email_welcome_body",
    }
    client = TestClient(app_no_save_permission)
    r = client.post(
        "/v1/notifications/email",
        json=payload,
        headers={
            "Authorization": "Bearer x",
            "language": "es",
            "timezone": "America/Bogota",
        },
    )
    assert r.status_code in (401, 403)
