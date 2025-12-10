from typing import Annotated

from app.dto.auth import (
    RegisterRequest,
    RegisterResponse,
    Token,
    UpdateUserRequest,
    UserResponse,
)
from app.services.auth import AuthServiceDep, CurrentUser
from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/auth")


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    auth_service: AuthServiceDep,
) -> RegisterResponse:
    return auth_service.register_user(request)


# TODO: add explicit /login


@router.post("/token")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
) -> Token:
    """
    **Note:** Use email address in the 'username' field.
    """
    return auth_service.login_user(
        email=form_data.username, password=form_data.password
    )


@router.get("/me")
def get_profile(
    current_user: CurrentUser, auth_service: AuthServiceDep
) -> UserResponse:
    return auth_service.get_profile(current_user)


@router.patch("/me")
def update_profile(
    request: UpdateUserRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
) -> UserResponse:
    return auth_service.update_profile(current_user, request)


@router.get("/me/avatar")
def get_avatar(current_user: CurrentUser, auth_service: AuthServiceDep) -> FileResponse:
    return auth_service.get_avatar(current_user)


@router.put("/me/avatar", status_code=status.HTTP_204_NO_CONTENT)
def upload_avatar(
    file: UploadFile, current_user: CurrentUser, auth_service: AuthServiceDep
):
    return auth_service.upload_avatar(current_user, file)


@router.delete("/me/avatar", status_code=status.HTTP_204_NO_CONTENT)
def delete_avatar(current_user: CurrentUser, auth_service: AuthServiceDep):
    return auth_service.delete_avatar(current_user)
