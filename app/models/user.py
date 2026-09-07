import uuid
from sqlalchemy import Column, String
from app.database.connection import Base


class User(Base):

    __tablename__ = "users"

    id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True
    )

    name = Column(
        String(50),
        nullable=False
    )

    surname = Column(
        String(50),
        nullable=False
    )

    phone = Column(
        String(10),
        unique=True,
        nullable=False
    )

    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String(255),
        nullable=False
    )

    role = Column(
        String(20),
        nullable=False,
        default="user"
    )

    pincode = Column(
        String(32),
        nullable=False
    )