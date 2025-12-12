import secrets

DATABASE_URL = "sqlite:///app.db"

API_V1_STR = "/api/v1"

JWT_SECRET_KEY = secrets.token_urlsafe(32)
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60  # 1 hour

# File upload settings
UPLOADS_DIR = "uploads/"
AVATAR_UPLOAD_DIR = UPLOADS_DIR + "avatars"
BANNER_UPLOAD_DIR = UPLOADS_DIR + "banners"
MAX_AVATAR_SIZE_MB = 5
MAX_BANNER_SIZE_MB = 10
MAX_BANNERS_PER_EVENT = 5
