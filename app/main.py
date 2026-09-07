from fastapi import FastAPI

from app.database.connection import (
    Base,
    engine
)

from app.models.user import User
from app.models.session import UserSession
from app.models.otp import PasswordOTP
from app.models.access_token import AccessToken

from app.routes.auth import (
    router as auth_router
)

from app.routes.user import (
    router as user_router
)

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="FastAPI Authentication API",
    version="1.0.0",
    description="""
    FastAPI Authentication API

    Authentication supports:

    - JWT Access Token
    - HTTP Bearer Authentication
    - Cookie Authentication
    - Session Management
    - OTP Password Reset
    - Swagger Authorization
    """
)

app.include_router(
    auth_router
)

app.include_router(
    user_router
)

@app.get(
    "/",
    tags=["Home"]
)
def home():

    return {
        "message": "Authentication API is running"
    }