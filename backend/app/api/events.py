from app.dto.events import EventResponse
from app.dto.pagination import PaginationParams
from app.dto.seats import SeatsResponse
from app.services.auth import OptionalCurrentUser
from app.services.events import EventServiceDep
from app.services.seats import SeatServiceDep
from fastapi import APIRouter
from fastapi_pagination import Page

router = APIRouter(prefix="/events")


@router.get("", description="List all events with pagination")
def list_all_events(
    params: PaginationParams,
    events_service: EventServiceDep,
    current_user: OptionalCurrentUser = None,
) -> Page[EventResponse]:
    return events_service.list_all_events(params, current_user)


@router.get("/{event_id}", description="Get details of a specific event by its ID")
def get_event(
    event_id: int,
    events_service: EventServiceDep,
    current_user: OptionalCurrentUser = None,
) -> EventResponse:
    return events_service.get_event(event_id, current_user)


@router.get(
    "/{event_id}/seats",
    description="Get all seats for an event with availability and pricing information",
)
def get_event_seats(event_id: int, seats_service: SeatServiceDep) -> SeatsResponse:
    return seats_service.get_event_seats(event_id)
