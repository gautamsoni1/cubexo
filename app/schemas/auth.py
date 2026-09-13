from typing import Optional
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
    model_validator
)
import re

class RegisterRequest(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=50
    )

    surname: str = Field(
        min_length=2,
        max_length=50
    )

    phone: str = Field(
        min_length=10,
        max_length=10
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=72
    )
    pincode: Optional[str] = Field(
        min_length=6,
        max_length=6
    )


    @field_validator("name", "surname")
    @classmethod
    def validate_name(cls, value):

        value = value.strip()

        if not re.fullmatch(
            r"[A-Za-z]+(?: [A-Za-z]+)*",
            value
        ):
            raise ValueError(
                "Name must contain only alphabets"
            )

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value):

        if not value.isdigit():
            raise ValueError(
                "Phone number must contain only digits"
            )

        if len(value) != 10:
            raise ValueError(
                "Phone number must contain exactly 10 digits"
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):

        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one number"
            )

        if not re.search(
            r"[!@#$%^&*(),.?\":{}|<>]",
            value
        ):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return value

    @model_validator(mode="after")
    def passwords_match(self):

        if self.password != self.confirm_password:

            raise ValueError(
                "Password and confirm password do not match"
            )

        return self

class LoginRequest(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=72
    )

class ForgotPasswordRequest(BaseModel):

    email: EmailStr

class VerifyOTPRequest(BaseModel):

    email: EmailStr

    otp: str = Field(
        min_length=6,
        max_length=6
    )

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value):

        if not value.isdigit():

            raise ValueError(
                "OTP must contain only digits"
            )

        return value

class ResetPasswordRequest(BaseModel):

    email: EmailStr

    new_password: str = Field(
        min_length=8,
        max_length=72
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=72
    )

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value):

        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one number"
            )

        if not re.search(
            r"[!@#$%^&*(),.?\":{}|<>]",
            value
        ):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return value

    @model_validator(mode="after")
    def passwords_match(self):

        if self.new_password != self.confirm_password:

            raise ValueError(
                "New password and confirm password do not match"
            )

        return self

class UserUpdate(BaseModel):
    name: str
    surname: str
    phone: str
    email: EmailStr
    password: str

class UserPatch(BaseModel):
    email: EmailStr | None = None
    