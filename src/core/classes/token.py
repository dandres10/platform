from fastapi import HTTPException
import jwt
from datetime import datetime, timedelta, timezone
from src.core.config import settings
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.access_token import AccessToken
from src.core.models.access_token_api import AccessTokenApi
from src.core.models.config import Config
from src.core.models.filter import FilterManager, Pagination
from src.domain.models.entities.api_token.api_token_read import ApiTokenRead
from src.domain.models.entities.user.user_read import UserRead
from src.domain.services.use_cases.entities.api_token.api_token_list_use_case import (
    ApiTokenListUseCase,
)
from src.domain.services.use_cases.entities.api_token.api_token_read_use_case import (
    ApiTokenReadUseCase,
)
from src.domain.services.use_cases.entities.user.user_read_use_case import (
    UserReadUseCase,
)
from src.infrastructure.database.repositories.entities.api_token_repository import (
    ApiTokenRepository,
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)

user_repository = UserRepository()
api_token_repository = ApiTokenRepository()


class Token:
    def __init__(
        self,
    ):
        self.secret_key = settings.jwt_secret_key
        self.algorithm = settings.jwt_algorithm
        self.user_read_use_case = UserReadUseCase(user_repository=user_repository)
        self.api_token_read_use_case = ApiTokenReadUseCase(
            api_token_repository=api_token_repository
        )
        self.api_token_list_use_case = ApiTokenListUseCase(
            api_token_repository=api_token_repository
        )

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

    def create_access_token_api(self, data: AccessTokenApi):
        to_encode = data
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

            return AccessToken(**decoded_token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail=f"Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail=f"Token invalido")
        except:
            return self.decode_token_api(token)

    def decode_token_api(self, token):
        try:
            decoded_token = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )

            return AccessTokenApi(**decoded_token)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail=f"Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail=f"Token invalido")

    def decode_token(self, token):
        try:
            decoded_token = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            return decoded_token
        except:
            return None

    def refresh_access_token(self, refresh_token, data: AccessToken):
        try:
            if not refresh_token:
                raise HTTPException(status_code=401, detail=f"Refresh token no existe")

            decoded_token = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )

            if decoded_token:
                new_access_token = self.create_access_token(data)
                return new_access_token
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail=f"Token expirado")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail=f"Token invalido")

    async def validate_has_refresh_token(self, config: Config):
        ##TODO validar si afecta de forma global
        config.response_type = RESPONSE_TYPE.OBJECT

        if not hasattr(config.token, "user_id"):
            return await self.validate_token_api(config=config)

        user_read = await self.user_read_use_case.execute(
            config=config, params=UserRead(id=config.token.user_id)
        )

        if not user_read.refresh_token:
            raise HTTPException(status_code=401, detail=f"Token expirado")

    async def validate_token_api(self, config: Config):
        config.response_type = RESPONSE_TYPE.OBJECT

        api_token_list = await self.api_token_list_use_case.execute(
            config=config,
            params=Pagination(
                all_data=True,
                filters=[
                    FilterManager(
                        field="token",
                        condition=CONDITION_TYPE.EQUALS.value,
                        value=config.encoded_token,
                    )
                ],
            ),
        )

        if isinstance(api_token_list, str):
            raise HTTPException(status_code=401, detail=f"Token api no valido")
