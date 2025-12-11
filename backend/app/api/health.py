from fastapi import APIRouter

from app.dto.health import HealthResponse

router = APIRouter()


@router.get("/health", description="Check the health status of the application")
def health_check() -> HealthResponse:
    return HealthResponse()
