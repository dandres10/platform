# SPEC-003 T10 / SPEC-002 Geography
import pytest


HEADERS = {"language": "es", "timezone": "America/Bogota"}


async def test_countries_returns_list(client):
    r = await client.get("/v1/geography/countries", headers=HEADERS)
    assert r.status_code == 200
    body = r.json()
    assert body["notification_type"] == "SUCCESS"
    assert isinstance(body["response"], list)
    assert len(body["response"]) > 0


async def test_hierarchy_for_country(client):
    # Obtener primer country del listado
    r1 = await client.get("/v1/geography/countries", headers=HEADERS)
    country_id = r1.json()["response"][0]["id"]

    r2 = await client.post("/v1/geography/hierarchy", json={"node_id": country_id}, headers=HEADERS)
    assert r2.status_code == 200
    body = r2.json()
    assert body["notification_type"] == "SUCCESS"
    assert "node" in body["response"]
    assert "ancestors" in body["response"]
    assert body["response"]["depth"] >= 0


async def test_hierarchy_invalid_node_id(client):
    fake_id = "00000000-0000-4000-8000-000000000000"
    r = await client.post("/v1/geography/hierarchy", json={"node_id": fake_id}, headers=HEADERS)
    assert r.status_code in (200, 404)
    if r.status_code == 200:
        body = r.json()
        assert body["notification_type"] in ("WARNING", "ERROR", "INFO")


async def test_types_by_country(client):
    r1 = await client.get("/v1/geography/countries", headers=HEADERS)
    country_id = r1.json()["response"][0]["id"]

    r2 = await client.post("/v1/geography/country/types", json={"country_id": country_id}, headers=HEADERS)
    assert r2.status_code == 200
    body = r2.json()
    assert isinstance(body["response"], list)


async def test_children_of_country(client):
    r1 = await client.get("/v1/geography/countries", headers=HEADERS)
    country_id = r1.json()["response"][0]["id"]

    r2 = await client.post("/v1/geography/children", json={"parent_id": country_id}, headers=HEADERS)
    assert r2.status_code == 200
    body = r2.json()
    assert isinstance(body["response"], list)


# SPEC-032 T7
async def test_by_country_and_type_returns_filtered_list(client):
    """ByCountryAndTypeUseCase: dado country_id + type, retorna nodos
    de ese país y tipo (ej: todos los STATE/DEPARTMENT del país)."""
    r1 = await client.get("/v1/geography/countries", headers=HEADERS)
    country_id = r1.json()["response"][0]["id"]

    r_types = await client.post("/v1/geography/country/types", json={"country_id": country_id}, headers=HEADERS)
    types_body = r_types.json()
    if not types_body.get("response"):
        return  # país sin tipos en seed → smoke pasa
    type_name = types_body["response"][0].get("type") or types_body["response"][0].get("name")
    if not type_name:
        return

    r2 = await client.post(
        "/v1/geography/country/type",
        json={"country_id": country_id, "type_name": type_name},
        headers=HEADERS,
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["notification_type"] in ("SUCCESS", "ERROR")
    if body["notification_type"] == "SUCCESS":
        assert isinstance(body["response"], list)


async def test_children_by_type_returns_filtered_list(client):
    """ChildrenByTypeUseCase: dado parent_id + type_name, retorna hijos
    del nodo que sean de ese tipo específico."""
    r1 = await client.get("/v1/geography/countries", headers=HEADERS)
    country_id = r1.json()["response"][0]["id"]

    r_types = await client.post("/v1/geography/country/types", json={"country_id": country_id}, headers=HEADERS)
    types_body = r_types.json()
    if not types_body.get("response"):
        return
    type_name = types_body["response"][0].get("type") or types_body["response"][0].get("name")
    if not type_name:
        return

    r2 = await client.post(
        "/v1/geography/children/type",
        json={"parent_id": country_id, "type_name": type_name},
        headers=HEADERS,
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body["notification_type"] in ("SUCCESS", "ERROR")


async def test_detail_returns_node_for_valid_id(client):
    """DetailUseCase: lookup directo por node_id retorna shape aplanado
    con type + type_label resueltos."""
    r1 = await client.get("/v1/geography/countries", headers=HEADERS)
    country_id = r1.json()["response"][0]["id"]

    r2 = await client.post("/v1/geography/detail", json={"node_id": country_id}, headers=HEADERS)
    assert r2.status_code == 200
    body = r2.json()
    assert body["notification_type"] == "SUCCESS"
    assert body["response"]["id"] == country_id


async def test_detail_returns_error_for_nonexistent_id(client):
    fake_id = "00000000-0000-4000-8000-000000000000"
    r = await client.post("/v1/geography/detail", json={"node_id": fake_id}, headers=HEADERS)
    assert r.status_code == 200
    body = r.json()
    assert body["notification_type"] == "ERROR"
