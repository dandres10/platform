import re

from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# SPEC-006 T8
PASSWORD_MIN_LENGTH = 8
_PASSWORD_HAS_UPPER = re.compile(r"[A-Z]")
_PASSWORD_HAS_DIGIT = re.compile(r"\d")


class PasswordPolicyError(ValueError):
    pass


class Password:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def check_password(password: str, hashed_password: str) -> bool:
        return pwd_context.verify(password, hashed_password)

    # SPEC-006 T8
    @staticmethod
    def validate_policy(password: str) -> str:
        if not isinstance(password, str):
            raise PasswordPolicyError("password must be a string")
        if len(password) < PASSWORD_MIN_LENGTH:
            raise PasswordPolicyError(
                f"password must be at least {PASSWORD_MIN_LENGTH} characters"
            )
        if not _PASSWORD_HAS_UPPER.search(password):
            raise PasswordPolicyError(
                "password must contain at least one uppercase letter"
            )
        if not _PASSWORD_HAS_DIGIT.search(password):
            raise PasswordPolicyError(
                "password must contain at least one digit"
            )
        return password
