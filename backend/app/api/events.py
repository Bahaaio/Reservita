from app.dto.events import EventResponse
from app.dto.pagination import PaginationParams
from app.services.auth import OptionalCurrentUser
from app.services.events import EventServiceDep
from fastapi import APIRouter
from fastapi_pagination import Page

router = APIRouter(prefix="/events")


@router.get("")
def list_all_events(
    params: PaginationParams,
    events_service: EventServiceDep,
    current_user: OptionalCurrentUser = None,
) -> Page[EventResponse]:
    return events_service.list_all_events(params, current_user)


@router.get("/{event_id}")
def get_event(
    event_id: int,
    events_service: EventServiceDep,
    current_user: OptionalCurrentUser = None,
) -> EventResponse:
    return events_service.get_event(event_id, current_user)
