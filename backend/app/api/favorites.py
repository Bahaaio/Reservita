from app.dto.favorites import FavoriteRequest
from app.services.auth import CurrentUser
from app.services.favorites import FavoriteServiceDep
from fastapi import APIRouter, status

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Add an event to user's favorites",
)
def add_to_favorite(
    request: FavoriteRequest,
    current_user: CurrentUser,
    favorite_service: FavoriteServiceDep,
):
    favorite_service.add_to_favorites(current_user, request)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Remove an event from user's favorites",
)
def remove_from_favorite(
    request: FavoriteRequest,
    current_user: CurrentUser,
    favorite_service: FavoriteServiceDep,
):
    favorite_service.remove_from_favorites(current_user, request)
