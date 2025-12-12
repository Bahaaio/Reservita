from typing import Annotated

from app.core.config import settings
from app.core.security import (
    TokenData,
    create_access_token,
    decode_access_token,
    hash_password,
    oauth2_scheme,
    oauth2_scheme_optional,
    verify_password,
)
from app.db.models import User
from app.db.session import DBSession
from app.dto.auth import (
    RegisterRequest,
    RegisterResponse,
    Token,
    UpdateUserRequest,
    UserResponse,
)
from app.exceptions.auth import EmailAlreadyTakenError, InvalidCredentialsError
from app.util.files import (
    delete_file,
    get_avatar_path,
    get_image_response,
    save_file,
    validate_image_file,
)
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import select


class AuthService:
    def __init__(self, db: DBSession):
        self.db = db

    def register_user(self, request: RegisterRequest) -> RegisterResponse:
        user = self.db.exec(select(User).where(User.email == request.email)).first()

        if user is not None:
            raise EmailAlreadyTakenError()

        password_hash = hash_password(request.password)

        user = User(
            full_name=request.full_name,
            email=request.email,
            hashed_password=password_hash,
            phone_number=request.phone_number,
            is_agency=request.is_agency,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        token_data = TokenData(email=user.email)
        token = create_access_token(token_data)

        return RegisterResponse(user=UserResponse.model_validate(user), token=token)

    def login_user(self, email: str, password: str) -> Token:
        user = self.db.exec(select(User).where(User.email == email)).first()

        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        token_data = TokenData(email=user.email)
        return create_access_token(token_data)

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


def get_current_user(
    db: DBSession,
    token: str = Depends(oauth2_scheme),
) -> User:
    token_data = decode_access_token(token)
    user = db.exec(select(User).where(User.email == token_data.email)).first()

    if not user:
        raise InvalidCredentialsError()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_optional_current_user(
    db: DBSession, token: str | None = Depends(oauth2_scheme_optional)
) -> User | None:
    """Get current user if authenticated, else None. Never raises errors."""
    if not token:
        return None

    try:
        token_data = decode_access_token(token)
        user = db.exec(select(User).where(User.email == token_data.email)).first()
        return user
    except Exception:
        # Invalid or expired token - return None instead of raising
        return None


OptionalCurrentUser = Annotated[User | None, Depends(get_optional_current_user)]


def get_current_agency(current_user: CurrentUser) -> User:
    if not current_user.is_agency:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Agency access required")

    return current_user


CurrentAgency = Annotated[User, Depends(get_current_agency)]


def get_auth_service(db: DBSession) -> AuthService:
    return AuthService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
