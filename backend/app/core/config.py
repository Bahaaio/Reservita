from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = "sqlite:///app.db"

    # JWT/Auth
    SECRET_KEY: str = "d07bbefa967067a74274b4f615356a01eac34ce5efaced31ff1486a00be9bf00"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 60  # 1 hour

    # Upload
    UPLOAD_DIR: str = "uploads/"
    AVATAR_UPLOAD_DIR: str = UPLOAD_DIR + "avatars"
    BANNER_UPLOAD_DIR: str = UPLOAD_DIR + "banners"
    MAX_AVATAR_SIZE_MB: int = 5
    MAX_BANNER_SIZE_MB: int = 10
    MAX_BANNERS_PER_EVENT: int = 5

    # QR Code
    QR_CODE_BOX_SIZE: int = 8
    QR_CODE_BORDER_SIZE: int = 2


settings = Settings()
