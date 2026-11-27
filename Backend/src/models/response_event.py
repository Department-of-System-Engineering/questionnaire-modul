from sqlalchemy import BigInteger, Column, ForeignKey, Identity, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.database import Base


class ResponseEvent(Base):
    __tablename__ = "response_events"

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    response_id = Column(
        UUID(as_uuid=True),
        ForeignKey("responses.id", ondelete="CASCADE"),
        nullable=False,
    )
    t_utc_ns = Column(BigInteger, nullable=False)
    t_mono_ns = Column(BigInteger, nullable=False)
    type = Column(Text, nullable=False)
    payload = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
