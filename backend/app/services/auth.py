from typing import Annotated

from httpcore import request

from app.core.security import (
    AccessTokenData,
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
    ChangePasswordRequest,
)
from app.dto.users import UserResponse
from app.exceptions.auth import EmailAlreadyTakenError, InvalidCredentialsError
from fastapi import BackgroundTasks, Depends, HTTPException, status
from sqlmodel import select

from app.services.email import EmailServiceDep


class AuthService:
    def __init__(self, db: DBSession, email_service: EmailServiceDep):
        self.db = db
        self.email_service = email_service

    def register_user(
        self, request: RegisterRequest, background_tasks: BackgroundTasks
    ) -> RegisterResponse:
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

        token_data = AccessTokenData(email=user.email)
        token = create_access_token(token_data)

        # send welcome email
        background_tasks.add_task(self.email_service.send_welcome_email, user=user)

        return RegisterResponse(user=UserResponse.model_validate(user), token=token)

    def login_user(self, email: str, password: str) -> Token:
        user = self.db.exec(select(User).where(User.email == email)).first()

        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            raise InvalidCredentialsError()

        token_data = AccessTokenData(email=user.email)
        return create_access_token(token_data)
    
    def change_password(
        self, user: User, request: ChangePasswordRequest
    ):
        if not verify_password(request.old_password, user.hashed_password):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "Old password is incorrect"
            )
    
        if verify_password(request.new_password, user.hashed_password):
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "New password must be different from the old password" 
            )
    
        user.hashed_password = hash_password(request.new_password)
        self.db.add(user)
        self.db.commit()


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


def get_auth_service(db: DBSession, email_service: EmailServiceDep) -> AuthService:
    return AuthService(db, email_service)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


