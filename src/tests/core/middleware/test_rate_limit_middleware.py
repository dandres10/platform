# SPEC-029 T5
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.core.middleware.user_rate_limit_middleware import UserRateLimitMiddleware


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(UserRateLimitMiddleware)

    @app.post("/v1/auth/login")
    def login():
        return {"ok": True}

    @app.get("/v1/company-currency")
    def list_company_currency():
        return {"ok": True}

    @app.get("/health")
    def health():
        return {"ok": True}

    return app


def test_business_endpoint_returns_429_after_30_requests():
    client = TestClient(_build_app())
    headers = {"X-Forwarded-For": "10.0.0.1"}

    accepted = 0
    rejected = 0
    for _ in range(35):
        r = client.post("/v1/auth/login", headers=headers, json={})
        if r.status_code == 429:
            rejected += 1
        else:
            accepted += 1

    assert accepted == 30, f"expected 30 accepted, got {accepted}"
    assert rejected == 5, f"expected 5 rejected, got {rejected}"


def test_429_payload_shape_matches_response_contract():
    client = TestClient(_build_app())
    headers = {"X-Forwarded-For": "10.0.0.2"}
    for _ in range(30):
        client.post("/v1/auth/login", headers=headers, json={})

    r = client.post("/v1/auth/login", headers=headers, json={})
    assert r.status_code == 429
    body = r.json()
    assert body["notification_type"] == "ERROR"
    assert body["code"] == "RATE-001"
    assert body["message_type"] == "STATIC"
    assert body["response"] is None


def test_health_endpoint_is_exempt():
    client = TestClient(_build_app())
    for _ in range(50):
        r = client.get("/health")
        assert r.status_code == 200


def test_entity_endpoint_uses_higher_rate():
    client = TestClient(_build_app())
    headers = {"X-Forwarded-For": "10.0.0.20"}

    for i in range(120):
        r = client.get("/v1/company-currency", headers=headers)
        assert r.status_code == 200, f"request {i} got {r.status_code}"

    r = client.get("/v1/company-currency", headers=headers)
    assert r.status_code == 429
