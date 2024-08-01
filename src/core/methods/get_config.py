from fastapi import HTTPException, Request
from src.core.models.config import Config
from src.infrastructure.database.config.config_db import session_db


def get_config(request: Request) -> Config:
    config = Config()
    # tokenManager = TokenManager()

    # if "authorization" not in request.headers:
    #    raise HTTPException(
    #        status_code=400, detail="Does not have authorization in the header"
    #    )
    # if "header_language" not in request.headers:
    #    raise HTTPException(
    #        status_code=400, detail="Does not have header_language in the header"
    #    )

    # languages = [LANGUAGES.EN.value, LANGUAGES.ES.value]

    # tokenHeader = request.headers["authorization"].split(" ")[1]
    # header_language = request.headers["header_language"]

    # if not header_language in languages:
    #    raise HTTPException(status_code=400, detail="Invalid language")

    # token = tokenManager.decode_token(tokenHeader)
    # config = token
    config.db = session_db()
    # config["header_language"] = header_language

    return config
