from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from app.database.connection import Base


class AccessToken(Base):

    __tablename__ = "access_tokens"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False
    )

    token_hash = Column(
        String,
        nullable=False,
        unique=True,
        index=True
    )

    token_type = Column(
        String(20),
        nullable=False,
        default="access"
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )
