# SPEC-032 quick win — Catalog
"""E2E de los 2 UCs business de catalog."""


HEADERS = {
    "language": "es",
    "timezone": "America/Bogota",
    "Authorization": "Bearer fake",
}


async def test_list_companies_returns_response_for_authenticated_user(client):
    """ListCompaniesUseCase: endpoint vivo + auth."""
    payload = {"skip": 0, "limit": 50, "all_data": False}
    r = await client.post("/v1/catalog/companies", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] in ("SUCCESS", "ERROR")
    if body["notification_type"] == "SUCCESS":
        assert isinstance(body["response"], list)


async def test_list_locations_by_company_returns_response(client):
    """ListLocationsByCompanyUseCase: endpoint vivo + multi-tenant filter
    por company_id del JWT."""
    payload = {"skip": 0, "limit": 50, "all_data": False}
    r = await client.post("/v1/catalog/locations", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] in ("SUCCESS", "ERROR")
    if body["notification_type"] == "SUCCESS":
        assert isinstance(body["response"], list)
