from fastapi import APIRouter

from app.dto.health import HealthResponse

router = APIRouter()


@router.get("/health")
def health_check() -> HealthResponse:
    return HealthResponse()
