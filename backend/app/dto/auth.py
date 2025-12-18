from app.dto.users import UserResponse
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    expires_in: int  # expiration in seconds
    token_type: str = "bearer"


# TODO: add validation rules
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str = Field(min_length=8)
    phone_number: str
    is_agency: bool


class RegisterResponse(BaseModel):
    user: UserResponse
    token: Token


class ChangePasswordRequest(BaseModel):
    old_password: str = Field(min_length=8)
    new_password: str = Field(min_length=8)
