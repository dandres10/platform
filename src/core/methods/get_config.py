from fastapi import Depends, HTTPException, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.core.classes.token import Token
from src.core.enums.language import LANGUAGE
from src.core.models.config import Config
from src.infrastructure.database.config.config_db import session_db


bearer_scheme = HTTPBearer()


def get_config(
    request: Request,
    language: str = Header(...),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> Config:
    config = Config()
    token_cls = Token() 
    valid_language_header(request=request)

    token = credentials.credentials
    token = token_cls.verify_token(token=token)

    config.db = session_db()
    config.language = language
    config.request = request
    config.token = token

    return config


def get_config_login(request: Request, language: str = Header(...)) -> Config:
    config = Config()
    valid_language_header(request=request)
    config.db = session_db()
    config.language = language
    config.request = request

    return config


def valid_language_header(request: Request):
    if "language" not in request.headers:
        raise HTTPException(
            status_code=400, detail="Does not have language in the header"
        )

    languages = [LANGUAGE.EN.value, LANGUAGE.ES.value]

    if not request.headers["language"] in languages:
        raise HTTPException(status_code=400, detail="Invalid language")
