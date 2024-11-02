from sqlalchemy.sql import func
from src.core.models.base import Base
from sqlalchemy import Column, String, Boolean, DateTime, text, Text, Integer, Float, Time
from sqlalchemy.dialects.postgresql import UUID

class TranslationEntity(Base):
    __tablename__ = 'translation'

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False, server_default=text('uuid_generate_v4()'))
    key = Column(String(255), nullable=False)
    language_code = Column(String(10), nullable=False)
    translation = Column(Text, nullable=False)
    context = Column(String(255), nullable=True)
    state = Column(Boolean, nullable=False, server_default=text('true'))
    created_date = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_date = Column(DateTime, nullable=False, server_default=text('now()'), onupdate=text('now()'))
