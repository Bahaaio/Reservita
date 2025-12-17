from datetime import datetime, timedelta, timezone

import jwt
from app.core.config import settings
from app.dto.auth import Token
from app.exceptions.auth import ExpiredTokenError, InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from pydantic import BaseModel, EmailStr

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=settings.API_V1_STR + "/auth/token")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=settings.API_V1_STR + "/auth/token", auto_error=False
)


class AccessTokenData(BaseModel):
    email: EmailStr


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return password_hash.verify(raw_password, hashed_password)


def encode_jwt(data: dict, expires_at: datetime) -> str:
    to_encode = data.copy()
    to_encode.update({"exp": expires_at})
    return jwt.encode(to_encode, settings.SECRET_KEY, settings.JWT_ALGORITHM)


def decode_jwt(token: str) -> dict:
    try:
        return jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError()
    except Exception:
        # catch all other exceptions as invalid token
        raise InvalidTokenError()


def create_access_token(data: AccessTokenData) -> Token:
    expires_delta = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    expires_at = datetime.now(timezone.utc) + expires_delta

    token = encode_jwt(data.model_dump(), expires_at=expires_at)

    return Token(access_token=token, expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS)


def decode_access_token(token: str) -> AccessTokenData:
    payload = decode_jwt(token)

    try:
        return AccessTokenData.model_validate(payload)
    except Exception:
        raise InvalidTokenError()


class QRCodeData(BaseModel):
    user_id: int
    ticket_id: int
    event_id: int


def create_qr_code_token(
    user_id: int,
    ticket_id: int,
    event_id: int,
    expires_at: datetime,
) -> str:
    data = QRCodeData(
        user_id=user_id,
        ticket_id=ticket_id,
        event_id=event_id,
    )

    return encode_jwt(data.model_dump(), expires_at=expires_at)


def decode_qr_code_token(token: str) -> QRCodeData:
    payload = decode_jwt(token)

    try:
        return QRCodeData.model_validate(payload)
    except Exception:
        raise InvalidTokenError()
