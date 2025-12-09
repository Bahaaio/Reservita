from typing import Annotated

from app.core.security import (
    TokenData,
    create_access_token,
    decode_access_token,
    hash_password,
    oauth2_scheme,
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
from fastapi import Depends
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


def get_current_user(
    db: DBSession,
    token: str = Depends(oauth2_scheme),
) -> User:
    token_data = decode_access_token(token)
    email = token_data.email
    user = db.exec(select(User).where(User.email == email)).first()

    if not user:
        raise InvalidCredentialsError()

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_auth_service(db: DBSession) -> AuthService:
    return AuthService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
