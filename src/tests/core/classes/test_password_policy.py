# SPEC-006 T8
import pytest

from src.core.classes.password import (
    PASSWORD_MIN_LENGTH,
    Password,
    PasswordPolicyError,
)


class TestPasswordPolicyValid:

    def test_min_length_uppercase_digit_passes(self):
        assert Password.validate_policy("Abcdef12") == "Abcdef12"

    def test_long_password_with_special_chars_passes(self):
        assert (
            Password.validate_policy("Str0ng!P@ssw0rd")
            == "Str0ng!P@ssw0rd"
        )

    def test_password_returns_unchanged_value(self):
        result = Password.validate_policy("MyP4ssword")
        assert result == "MyP4ssword"


class TestPasswordPolicyInvalid:

    def test_too_short_fails(self):
        with pytest.raises(PasswordPolicyError, match="at least 8 characters"):
            Password.validate_policy("Ab12")

    def test_no_uppercase_fails(self):
        with pytest.raises(PasswordPolicyError, match="uppercase"):
            Password.validate_policy("nouppercase1")

    def test_no_digit_fails(self):
        with pytest.raises(PasswordPolicyError, match="digit"):
            Password.validate_policy("NoDigitsHere")

    def test_empty_string_fails(self):
        with pytest.raises(PasswordPolicyError):
            Password.validate_policy("")

    def test_non_string_fails(self):
        with pytest.raises(PasswordPolicyError, match="must be a string"):
            Password.validate_policy(12345678)

    def test_only_whitespace_fails(self):
        with pytest.raises(PasswordPolicyError, match="uppercase"):
            Password.validate_policy("        ")


class TestPasswordPolicyConstants:

    def test_min_length_is_eight(self):
        assert PASSWORD_MIN_LENGTH == 8


class TestPasswordPolicyAsPydanticValidator:
    """validate_policy es reusable como pydantic field_validator."""

    def test_pydantic_v2_field_validator_integration(self):
        from pydantic import BaseModel, field_validator

        class _TestModel(BaseModel):
            new_password: str

            @field_validator("new_password")
            @classmethod
            def _validate(cls, v: str) -> str:
                return Password.validate_policy(v)

        ok = _TestModel(new_password="Abcdef12")
        assert ok.new_password == "Abcdef12"

        with pytest.raises(Exception) as exc:
            _TestModel(new_password="weak")
        assert "at least 8 characters" in str(exc.value)
