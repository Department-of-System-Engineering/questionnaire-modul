from sqlalchemy import (
    BigInteger, Column, DateTime, ForeignKey, ForeignKeyConstraint,
    Integer, Text, func, text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.database import Base


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (
        ForeignKeyConstraint(
            ["questionnaire_id", "version"],
            ["questionnaire_versions.questionnaire_id", "questionnaire_versions.version"],
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    participant_pseudonym = Column(Text, nullable=False)
    session_ref = Column(Text)
    group_ref = Column(Text)
    questionnaire_id = Column(Text, nullable=False)
    version = Column(Text, nullable=False)
    occasion = Column(Text, nullable=False)          # 'pre' | 'post' | 'between_cycles'
    cycle_number = Column(Integer)                   # only set for 'between_cycles'
    language = Column(Text, nullable=False)
    seed = Column(BigInteger, nullable=False)
    item_order = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    status = Column(Text, nullable=False, server_default="in_progress")
    started_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
    answers = Column(JSONB, nullable=False, server_default=text("'[]'::jsonb"))
