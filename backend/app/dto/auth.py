from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    access_token: str
    expires_in: int  # expiration in seconds
    token_type: str = "bearer"


class UserResponse(BaseModel):
    full_name: str
    email: str
    phone_number: str
    is_agency: bool

    class Config:
        from_attributes = True


class UpdateUserRequest(BaseModel):
    full_name: str | None = None
    phone_number: str | None = None


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
