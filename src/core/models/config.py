from typing import Any, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

class Config(BaseModel):
    db: Optional[Any] = None
    language: Optional[str] = None




