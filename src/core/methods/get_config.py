from fastapi import HTTPException, Header, Request
from src.core.enums.language import LANGUAGE
from src.core.models.config import Config
from src.infrastructure.database.config.config_db import session_db


def get_config(request: Request, language: str = Header(...)) -> Config:
    config = Config()
    valid_language_header(request=request)
    # tokenManager = TokenManager()

    # if "authorization" not in request.headers:
    #    raise HTTPException(
    #        status_code=400, detail="Does not have authorization in the header"
    #    )

    # tokenHeader = request.headers["authorization"].split(" ")[1]
    # header_language = request.headers["header_language"]

    # token = tokenManager.decode_token(tokenHeader)
    # config = token
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
