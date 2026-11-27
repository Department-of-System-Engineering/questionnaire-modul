from sqlalchemy import Boolean, Column, DateTime, Identity, Integer, Text, func

from src.database import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, Identity(always=True), primary_key=True)
    name = Column(Text, nullable=False, unique=True)
    key_hash = Column(Text, nullable=False, unique=True)
    active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
