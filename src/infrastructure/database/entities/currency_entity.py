from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class CurrencyEntity(Base):
    __tablename__ = "currency"
    
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    name = Column(String(255), nullable=False)
    code = Column(String(10), unique=True, nullable=False)
    symbol = Column(String(10), nullable=False)
    state = Column(Boolean, nullable=False, default=True, server_default=text("TRUE"))
    created_date = Column(DateTime, nullable=False, server_default=func.now())
    updated_date = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
