from typing import Annotated

from app.dto.auth import (
    RegisterRequest,
    RegisterResponse,
    Token,
)
from app.services.auth import AuthServiceDep
from fastapi import APIRouter, Form, status
from pydantic import EmailStr

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    description="Register a new user with email and password",
)
def register(
    request: RegisterRequest,
    auth_service: AuthServiceDep,
) -> RegisterResponse:
    return auth_service.register_user(request)


@router.post(
    "/token",
    description="OAuth2-compatible token endpoint. Use email in the 'username' field",
)
def login(
    username: Annotated[EmailStr, Form()],
    password: Annotated[str, Form(min_length=8)],
    auth_service: AuthServiceDep,
) -> Token:
    """**Note:** Use email address in the 'username' field."""
    return auth_service.login_user(username, password)
