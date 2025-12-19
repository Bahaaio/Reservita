from app.dto.events import EventResponse
from app.dto.favorites import FavoriteRequest
from app.services.auth import CurrentUser
from app.services.favorites import FavoriteServiceDep
from fastapi import APIRouter, status

router = APIRouter(prefix="/users/me/favorites", tags=["Favorites"])


@router.get(
    "",
    description="Get user's favorite events",
)
def get_favorites(
    current_user: CurrentUser,
    favorite_service: FavoriteServiceDep,
) -> list[EventResponse]:
    return favorite_service.get_favorites(current_user)


@router.post(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Add an event to user's favorites",
)
def add_to_favorite(
    request: FavoriteRequest,
    current_user: CurrentUser,
    favorite_service: FavoriteServiceDep,
):
    favorite_service.add_to_favorites(current_user, request)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Remove an event from user's favorites",
)
def remove_from_favorite(
    event_id: int,
    current_user: CurrentUser,
    favorite_service: FavoriteServiceDep,
):
    favorite_service.remove_from_favorites(current_user, event_id)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Remove all events from user's favorites",
)
def remove_all_favorites(
    current_user: CurrentUser,
    favorite_service: FavoriteServiceDep,
):
    favorite_service.remove_all_favorites(current_user)
