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


class TokenData(BaseModel):
    email: EmailStr


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return password_hash.verify(raw_password, hashed_password)


def create_access_token(data: TokenData) -> Token:
    to_encode = data.model_dump()

    expire_delta = timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS)
    expire_time = datetime.now(timezone.utc) + expire_delta

    to_encode.update({"exp": expire_time})

    return Token(
        access_token=jwt.encode(to_encode, settings.SECRET_KEY, settings.JWT_ALGORITHM),
        expires_in=settings.ACCESS_TOKEN_EXPIRE_SECONDS,
    )


def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return TokenData(email=payload.get("email"))

    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError()
    except Exception:
        # catch all other exceptions as invalid token
        raise InvalidTokenError()
