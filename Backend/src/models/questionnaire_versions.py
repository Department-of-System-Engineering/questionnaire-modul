from sqlalchemy import Column, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from src.database import Base

class QuestionnaireVersion(Base):
    __tablename__ = "questionnaire_versions"

    questionnaire_id = Column(String, primary_key=True)
    version = Column(String, primary_key=True)
    name = Column(JSONB, nullable=False)
    hash = Column(String, nullable=False)
    languages = Column(ARRAY(Text), nullable=False)
    definition = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)