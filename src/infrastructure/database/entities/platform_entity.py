from datetime import datetime
from pydantic import UUID4
from sqlalchemy import DateTime, func, text
from sqlalchemy.orm import Mapped, mapped_column
from src.core.models.base import Base


class PlatformEntity(Base):
    __tablename__ = "platform"
    id: Mapped[str] = mapped_column(
        primary_key=True, server_default=text("uuid_generate_v4()")
    )
    language: Mapped[UUID4] = mapped_column(nullable=False)
    created_date: Mapped[datetime] = mapped_column(
        DateTime, insert_default=func.now(), nullable=False
    )
    updated_date: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
