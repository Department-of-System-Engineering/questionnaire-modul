from sqlalchemy import (
    BigInteger, Boolean, Column, ForeignKeyConstraint, Identity,
    Integer, Text, UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB

from src.database import Base


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["questionnaire_id", "version"],
            ["questionnaire_versions.questionnaire_id", "questionnaire_versions.version"],
            ondelete="CASCADE",
        ),
        UniqueConstraint("questionnaire_id", "version", "item_id"),
    )

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    questionnaire_id = Column(Text, nullable=False)
    version = Column(Text, nullable=False)
    item_id = Column(Text, nullable=False)          # the "id" from the JSON
    page_id = Column(Text, nullable=False)
    position = Column(Integer, nullable=False)
    type = Column(Text, nullable=False)
    required = Column(Boolean, nullable=False, server_default="false")
    definition = Column(JSONB, nullable=False)
