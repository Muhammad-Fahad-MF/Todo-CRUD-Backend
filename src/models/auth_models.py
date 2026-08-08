import re
import unicodedata
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

class User(BaseModel):
    id: str
    name: str | None = None
    email: str
    created_at: datetime

class SignupReq(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="User full name")
    email: EmailStr = Field(max_length=255, description="User email address")
    password: str = Field(min_length=8, max_length=72, description="Raw password")

    @field_validator("name", mode="before")
    @classmethod
    def sanitize_name(cls, value: str) -> str:
        if isinstance(value, str):
            cleaned = re.sub(r"\s+", " ", value.strip())
            return unicodedata.normalize("NFC", cleaned)
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("password")
    @classmethod
    def enforce_password_security(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 bytes.")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one digit.")
        # if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>/?]', value):
        #     raise ValueError("Password must contain at least one special character.")
            
        return value

    @model_validator(mode="after")
    def prevent_password_context_leak(self) -> "SignupReq":
        email_prefix = self.email.split("@")[0].lower()
        password_lower = self.password.lower()
        
        if len(email_prefix) > 3 and email_prefix in password_lower:
            raise ValueError("Password cannot contain your email username.")
            
        if len(self.name) > 2 and self.name.lower() in password_lower:
            raise ValueError("Password cannot contain your name.")
            
        return self


class LoginReq(BaseModel):
    email: EmailStr = Field(max_length=255, description="User email address")
    password: str = Field(min_length=8, max_length=72, description="Raw password")

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip().lower()
        return value


class LoginRes(BaseModel):
    user_id: str
    email: str
    display_name: str
    access_token: str


class SignupRes(BaseModel):
    user_id: str
    email: str
    display_name: str
    