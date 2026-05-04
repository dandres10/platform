# SPEC-006 T7
"""Tests para /password-reset-token entity router."""
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.models.response import Response
from src.tests._mock_utils import make_async_db_mock


class MockToken:
    def __init__(self):
        self.permissions = [p.value for p in PERMISSION_TYPE]
        self.user_id = str(uuid4())
        self.company_id = str(uuid4())
        self.location_id = str(uuid4())
        self.rol_code = "ADMIN"


class MockConfig:
    def __init__(self):
        self.token = MockToken()
        self.async_db = make_async_db_mock()
        self.response_type = "dict"
        self.language = "es"


def get_mock_config():
    return MockConfig()


@pytest.fixture
def app():
    from src.core.methods.get_config import get_config
    from src.infrastructure.web.entities_routes.password_reset_token_router import (
        password_reset_token_router,
    )

    test_app = FastAPI()
    test_app.include_router(password_reset_token_router)
    test_app.dependency_overrides[get_config] = get_mock_config
    return test_app


@pytest.fixture
def client(app):
    return TestClient(app)


def _save_payload():
    return {
        "user_id": str(uuid4()),
        "token": "abc123def456",
        "expires_at": (datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)).isoformat(),
        "state": True,
    }


def _update_payload():
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "token": "updated_token",
        "expires_at": (datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)).isoformat(),
        "used_at": None,
        "state": True,
    }


class TestPasswordResetTokenRouter:

    def test_save_invalid_body_returns_422(self, client):
        response = client.post("/password-reset-token", json={})
        assert response.status_code == 422

    def test_update_invalid_body_returns_422(self, client):
        response = client.put("/password-reset-token", json={})
        assert response.status_code == 422

    def test_delete_invalid_uuid_returns_422(self, client):
        response = client.delete("/password-reset-token/not-a-uuid")
        assert response.status_code == 422

    def test_read_invalid_uuid_returns_422(self, client):
        response = client.get("/password-reset-token/not-a-uuid")
        assert response.status_code == 422

    @patch(
        "src.infrastructure.web.entities_routes.password_reset_token_router.password_reset_token_controller"
    )
    def test_save_success(self, mock_ctrl, client):
        mock_ctrl.save = AsyncMock(
            return_value=Response.success_temporary_message(
                response={"id": str(uuid4())}, message="OK"
            )
        )
        response = client.post("/password-reset-token", json=_save_payload())
        assert response.status_code == 200

    @patch(
        "src.infrastructure.web.entities_routes.password_reset_token_router.password_reset_token_controller"
    )
    def test_update_success(self, mock_ctrl, client):
        mock_ctrl.update = AsyncMock(
            return_value=Response.success_temporary_message(
                response={"id": str(uuid4())}, message="OK"
            )
        )
        response = client.put("/password-reset-token", json=_update_payload())
        assert response.status_code == 200

    @patch(
        "src.infrastructure.web.entities_routes.password_reset_token_router.password_reset_token_controller"
    )
    def test_list_success(self, mock_ctrl, client):
        mock_ctrl.list = AsyncMock(
            return_value=Response.success_temporary_message(response=[], message="OK")
        )
        response = client.post(
            "/password-reset-token/list",
            json={"skip": 0, "limit": 10, "all_data": False},
        )
        assert response.status_code == 200

    @patch(
        "src.infrastructure.web.entities_routes.password_reset_token_router.password_reset_token_controller"
    )
    def test_read_success(self, mock_ctrl, client):
        mock_ctrl.read = AsyncMock(
            return_value=Response.success_temporary_message(
                response={"id": str(uuid4())}, message="OK"
            )
        )
        response = client.get(f"/password-reset-token/{uuid4()}")
        assert response.status_code == 200

    @patch(
        "src.infrastructure.web.entities_routes.password_reset_token_router.password_reset_token_controller"
    )
    def test_delete_success(self, mock_ctrl, client):
        mock_ctrl.delete = AsyncMock(
            return_value=Response.success_temporary_message(
                response={"id": str(uuid4())}, message="OK"
            )
        )
        response = client.delete(f"/password-reset-token/{uuid4()}")
        assert response.status_code == 200
