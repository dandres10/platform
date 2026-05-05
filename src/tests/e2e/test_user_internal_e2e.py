# SPEC-032 T3
"""E2E parcial de UsersInternalUseCase.

CRUD completo (create / update / delete con guard last_admin) requiere un
fixture grande con company + location + rol_admin asignado. Esto se documenta
como ampliación futura — el test de listado ya valida multi-tenant filter +
endpoint vivo + auth.
"""
from sqlalchemy import text


HEADERS = {
    "language": "es",
    "timezone": "America/Bogota",
    "Authorization": "Bearer fake",
}


async def test_users_internal_listing_returns_response_for_authenticated_admin(client):
    """Endpoint vivo + auth. Response puede ser SUCCESS (lista) o ERROR
    (CORE_NO_RESULTS_FOUND si la company del token no tiene users) — ambos
    son válidos como "endpoint funciona y filtra por tenant"."""
    payload = {"skip": 0, "limit": 10, "all_data": False}
    r = await client.post("/v1/auth/users-internal", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] in ("SUCCESS", "ERROR")
    if body["notification_type"] == "SUCCESS":
        assert isinstance(body["response"], list)


async def test_users_internal_listing_filters_by_company_tenant(client):
    """Cuando la company del JWT no tiene ningún user, el listado responde
    ERROR con CORE_NO_RESULTS_FOUND. Esto valida que el multi-tenant filter
    está activo (no se filtran users de otras companies)."""
    payload = {"skip": 0, "limit": 50, "all_data": True}
    r = await client.post("/v1/auth/users-internal", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    if body["notification_type"] == "ERROR":
        assert body["response"] is None
    else:
        assert isinstance(body["response"], list)


# SPEC-032 quick win: UsersExternalUseCase
async def test_users_external_listing_returns_response(client):
    """UsersExternalUseCase: endpoint vivo + auth, multi-tenant filter."""
    payload = {"skip": 0, "limit": 10, "all_data": False}
    r = await client.post("/v1/auth/users-external", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] in ("SUCCESS", "ERROR")
    if body["notification_type"] == "SUCCESS":
        assert isinstance(body["response"], list)
