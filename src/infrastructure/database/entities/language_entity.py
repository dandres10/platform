
from sqlalchemy.sql import func
from src.core.models.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import  Column, String, Boolean, DateTime, text

class LanguageEntity(Base):
    __tablename__ = "language"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    native_name = Column(String(100), nullable=True)
    state = Column(Boolean, nullable=False, default=True, server_default=text("TRUE"))
    created_date = Column(DateTime, nullable=False, server_default=func.now())
    updated_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())