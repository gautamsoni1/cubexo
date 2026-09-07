from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean
)
from app.database.connection import Base
class PasswordOTP(Base):

    __tablename__ = "password_otps"

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

    otp_hash = Column(
        String(255),
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    verified = Column(
        Boolean,
        default=False,
        nullable=False
    )