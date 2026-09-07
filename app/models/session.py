from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from app.database.connection import Base


class UserSession(Base):

    __tablename__ = "user_sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    session_id = Column(
        String(128),
        unique=True,
        index=True,
        nullable=False
    )

    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )