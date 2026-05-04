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
