from typing import Annotated

from app.core.config import settings
from app.db.models import User
from app.db.session import DBSession
from app.dto.users import UpdateUserRequest, UserResponse
from app.util.files import (
    delete_file,
    get_avatar_path,
    get_image_response,
    save_file,
    validate_image_file,
)
from fastapi import Depends, UploadFile
from fastapi.responses import FileResponse


class UserService:
    def __init__(self, db: DBSession):
        self.db = db

    def get_profile(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    def update_profile(self, user: User, request: UpdateUserRequest) -> UserResponse:
        user.sqlmodel_update(request.model_dump(exclude_unset=True))

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return UserResponse.model_validate(user)

    def get_avatar(self, user: User) -> FileResponse:
        assert user.id is not None
        return get_image_response(get_avatar_path(user.id))

    def upload_avatar(self, user: User, file: UploadFile):
        validate_image_file(file, max_size_mb=settings.MAX_AVATAR_SIZE_MB)
        assert user.id is not None
        save_file(file, get_avatar_path(user.id))

    def delete_avatar(self, user: User):
        assert user.id is not None
        delete_file(get_avatar_path(user.id))


def get_user_service(db: DBSession) -> UserService:
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
