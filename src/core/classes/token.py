import jwt
from datetime import datetime, timedelta, timezone
from src.core.config import settings
from src.core.models.access_token import AccessToken


class Token:
    def __init__(
        self,
    ):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm

    def create_access_token(self, data: AccessToken):
        expiration = datetime.now(timezone.utc) + timedelta(
            minutes=data.token_expiration_minutes
        )
        to_encode = data
        to_encode.exp = expiration

        access_token = jwt.encode(
            to_encode.model_dump(), self.secret_key, algorithm=self.algorithm
        )
        return access_token

    def create_refresh_token(self, data: AccessToken):
        expiration = datetime.now(timezone.utc) + timedelta(
            minutes=(data.token_expiration_minutes + 2)
        )
        to_encode = data
        to_encode.exp = expiration
        refresh_token = jwt.encode(
            to_encode.model_dump(), self.secret_key, algorithm=self.algorithm
        )
        return refresh_token

    def verify_token(self, token):
        try:
            decoded_token = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return decoded_token
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def decode_token(self, token):
        try:
            decoded_token = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return decoded_token
        except:
            return None

    def refresh_access_token(self, refresh_token, body: dict):
        try:
            decoded_token = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )

            if decoded_token:
                new_access_token = self.create_access_token(body)
                return new_access_token
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
