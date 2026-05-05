# SPEC-032 T8
"""E2E del endpoint compartido POST /v1/notifications/email (SPEC-006 T3).

EmailServiceStub solo logea, no envía — los tests verifican el contrato
HTTP del endpoint (auth, validación de payload, resolución de templates).
"""
from uuid import uuid4

from sqlalchemy import text


HEADERS = {
    "language": "es",
    "timezone": "America/Bogota",
    "Authorization": "Bearer fake",
}


async def test_send_email_with_existing_template_returns_success(client):
    payload = {
        "to": "alice@test.com",
        "subject_key": "email_welcome_subject",
        "body_key": "email_welcome_body",
        "template_vars": {"name": "Alice"},
    }
    r = await client.post("/v1/notifications/email", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"
    assert body["response"] is True


async def test_send_email_with_nonexistent_subject_key_returns_error(client):
    payload = {
        "to": "alice@test.com",
        "subject_key": f"nonexistent_subject_{uuid4().hex[:8]}",
        "body_key": "email_welcome_body",
    }
    r = await client.post("/v1/notifications/email", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_send_email_validates_required_fields(client):
    """Pydantic 422 si faltan to/subject_key/body_key."""
    payload = {"to": "alice@test.com"}
    r = await client.post("/v1/notifications/email", json=payload, headers=HEADERS)
    assert r.status_code == 422


async def test_send_email_with_template_vars_substitutes(client):
    payload = {
        "to": "alice@test.com",
        "subject_key": "email_welcome_subject",
        "body_key": "email_welcome_body",
        "template_vars": {"name": "VarSubstitution Test"},
    }
    r = await client.post("/v1/notifications/email", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"


async def test_send_email_with_nonexistent_body_key_returns_error(client):
    """body_key inexistente (subject sí existe) → ERROR."""
    payload = {
        "to": "alice@test.com",
        "subject_key": "email_welcome_subject",
        "body_key": f"nonexistent_body_{uuid4().hex[:8]}",
    }
    r = await client.post("/v1/notifications/email", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"
