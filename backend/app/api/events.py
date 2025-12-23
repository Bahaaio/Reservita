from uuid import UUID

from app.dto.events import (
    EventResponse,
    FilterParams,
)
from app.dto.pagination import PaginationParams
from app.dto.seats import SeatsResponse
from app.services.auth import OptionalCurrentUser
from app.services.events import EventServiceDep
from app.services.seats import SeatServiceDep
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from fastapi_pagination import Page

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", description="List all events with optional filters and pagination")
def list_all_events(
    filters: FilterParams,
    params: PaginationParams,
    events_service: EventServiceDep,
    current_user: OptionalCurrentUser = None,
) -> Page[EventResponse]:
    return events_service.list_events(params, filters, current_user)


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


@router.get(
    "/banners/{banner_id}",
    description="Get the banner file of an existing event by its ID",
)
def get_banner(
    banner_id: UUID,
    events_service: EventServiceDep,
) -> StreamingResponse:
    return events_service.get_banner(banner_id)
