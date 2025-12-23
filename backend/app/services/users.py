from typing import Annotated

from app.db.models import User
from app.db.session import DBSession
from app.dto.users import UpdateUserRequest, UserResponse
from app.services.dependencies import StorageServiceDep
from app.util.files import (
    get_avatar_key,
    to_image_response,
)
from fastapi import Depends, UploadFile
from fastapi.responses import StreamingResponse


class UserService:
    def __init__(self, db: DBSession, storage_service: StorageServiceDep):
        self.db = db
        self.storage_service = storage_service

    def get_profile(self, user: User) -> UserResponse:
        return UserResponse.model_validate(user)

    def update_profile(self, user: User, request: UpdateUserRequest) -> UserResponse:
        user.sqlmodel_update(request.model_dump(exclude_unset=True))

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return UserResponse.model_validate(user)

    def get_avatar(self, user: User) -> StreamingResponse:
        assert user.id is not None
        key = get_avatar_key(user.id)
        avatar = self.storage_service.get(key)

        return to_image_response(avatar)

    def upload_avatar(self, user: User, file: UploadFile):
        assert user.id is not None
        key = get_avatar_key(user.id)
        self.storage_service.put(file, key)

    def delete_avatar(self, user: User):
        assert user.id is not None
        key = get_avatar_key(user.id)
        self.storage_service.delete(key)


def get_user_service(db: DBSession, storage_service: StorageServiceDep) -> UserService:
    return UserService(db, storage_service)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
