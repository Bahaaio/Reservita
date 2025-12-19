from app.dto.users import UserResponse
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    expires_in: int  # expiration in seconds
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=100)
    password: str = Field(min_length=8)
    phone_number: str = Field(
        min_length=7, max_length=15, pattern=r"^\+?[0-9\s\-\(\)]+$"
    )
    is_agency: bool


class RegisterResponse(BaseModel):
    user: UserResponse
    token: Token


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)
