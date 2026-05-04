# SPEC-028 T3
from src.core.wrappers.execute_transaction import _redact_sensitive, _SENSITIVE_KEYS


def test_redact_replaces_top_level_password():
    result = _redact_sensitive({"password": "secret", "email": "a@b.com"})
    assert result == {"password": "<redacted>", "email": "a@b.com"}


def test_redact_is_case_insensitive_for_authorization_header():
    payload = {"headers": {"Authorization": "Bearer xyz", "Content-Type": "json"}}
    result = _redact_sensitive(payload)
    assert result["headers"]["Authorization"] == "<redacted>"
    assert result["headers"]["Content-Type"] == "json"


def test_redact_lowercase_authorization_header():
    payload = {"headers": {"authorization": "Bearer xyz"}}
    assert _redact_sensitive(payload) == {"headers": {"authorization": "<redacted>"}}


def test_redact_recurses_into_nested_dicts():
    payload = {"route_info": {"json_body": {"password": "p"}, "query_params": {"token": "t"}}}
    result = _redact_sensitive(payload)
    assert result["route_info"]["json_body"]["password"] == "<redacted>"
    assert result["route_info"]["query_params"]["token"] == "<redacted>"


def test_redact_recurses_into_lists():
    payload = [{"password": "p"}, {"name": "ok"}]
    assert _redact_sensitive(payload) == [{"password": "<redacted>"}, {"name": "ok"}]


def test_redact_recurses_into_tuples():
    payload = ({"jwt_secret_key": "k"}, "safe")
    assert _redact_sensitive(payload) == ({"jwt_secret_key": "<redacted>"}, "safe")


def test_redact_does_not_mutate_input():
    original = {"password": "abc", "inner": {"api_token": "t"}}
    snapshot = {"password": "abc", "inner": {"api_token": "t"}}
    _redact_sensitive(original)
    assert original == snapshot


def test_redact_preserves_primitives():
    assert _redact_sensitive("hello") == "hello"
    assert _redact_sensitive(42) == 42
    assert _redact_sensitive(None) is None


def test_redact_covers_all_sensitive_keys():
    expected = {
        "password",
        "authorization",
        "token",
        "refresh_token",
        "secret_key",
        "jwt_secret_key",
        "access_token",
        "api_token",
    }
    assert _SENSITIVE_KEYS == expected


def test_redact_route_info_full_payload():
    error_info = {
        "error": "boom",
        "route_info": {
            "method": "POST",
            "url": "http://x/v1/auth/login",
            "headers": {"Authorization": "Bearer JWT", "Content-Type": "application/json"},
            "json_body": {"email": "a@b.com", "password": "super_secret"},
            "query_params": {"token": "t"},
        },
    }
    result = _redact_sensitive(error_info)
    assert result["error"] == "boom"
    assert result["route_info"]["headers"]["Authorization"] == "<redacted>"
    assert result["route_info"]["headers"]["Content-Type"] == "application/json"
    assert result["route_info"]["json_body"]["password"] == "<redacted>"
    assert result["route_info"]["json_body"]["email"] == "a@b.com"
    assert result["route_info"]["query_params"]["token"] == "<redacted>"
