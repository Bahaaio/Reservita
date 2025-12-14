from pydantic import BaseModel


class UpdateUserRequest(BaseModel):
    full_name: str | None = None
    phone_number: str | None = None


class UserResponse(BaseModel):
    full_name: str
    email: str
    phone_number: str
    is_agency: bool

    class Config:
        from_attributes = True
