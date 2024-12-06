from src.core.config import settings
from src.core.models.base import Base
from sqlalchemy import (
    Column,
    Boolean,
    DateTime,
    text,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID


class ApiTokenEntity(Base):
    __tablename__ = "api_token"
    __table_args__ = {"schema": settings.database_schema}

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        nullable=False,
        server_default=text("uuid_generate_v4()"),
    )
    rol_id = Column(UUID(as_uuid=True), nullable=False)
    token = Column(Text, nullable=False)
    state = Column(Boolean, nullable=False, server_default=text("true"))
    created_date = Column(DateTime, nullable=False, server_default=text("now()"))
    updated_date = Column(
        DateTime, nullable=False, server_default=text("now()"), onupdate=text("now()")
    )
