from app.dto.auth import ChangePasswordRequest
from app.dto.users import UpdateUserRequest, UserResponse
from app.services.auth import AuthServiceDep, CurrentUser
from app.services.users import UserServiceDep
from fastapi import APIRouter, UploadFile, status
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/users/me", tags=["Profile"])


@router.get("", description="Get the profile of the current user")
def get_profile(
    current_user: CurrentUser, user_service: UserServiceDep
) -> UserResponse:
    return user_service.get_profile(current_user)


@router.patch("", description="Update the profile of the current user")
def update_profile(
    request: UpdateUserRequest,
    current_user: CurrentUser,
    user_service: UserServiceDep,
) -> UserResponse:
    return user_service.update_profile(current_user, request)


@router.get("/avatar", description="Get the avatar of the current user")
def get_avatar(
    current_user: CurrentUser, user_service: UserServiceDep
) -> StreamingResponse:
    return user_service.get_avatar(current_user)


@router.put(
    "/avatar",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Upload or update the avatar of the current user (JPEG only, max 5MB)",
)
def upload_avatar(
    file: UploadFile,
    current_user: CurrentUser,
    user_service: UserServiceDep,
):
    return user_service.upload_avatar(current_user, file)


@router.delete(
    "/avatar",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete the avatar of the current user",
)
def delete_avatar(current_user: CurrentUser, user_service: UserServiceDep):
    return user_service.delete_avatar(current_user)


@router.patch(
    "/password",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Change the password of the current user",
)
def change_password(
    request: ChangePasswordRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
):
    auth_service.change_password(current_user, request)
