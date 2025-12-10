from app.dto.events import EventRequest, EventResponse
from app.dto.pagination import PaginationParams
from app.services.auth import CurrentAgency
from app.services.events import EventServiceDep
from fastapi import APIRouter
from fastapi_pagination import Page

router = APIRouter(prefix="/my-events")


@router.get("")
def list_my_events(
    params: PaginationParams,
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
) -> Page[EventResponse]:
    return events_service.list_agency_events(params, current_agency)


@router.post("")
def create_event(
    request: EventRequest,
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
) -> EventResponse:
    return events_service.create_event(current_agency, request)


@router.put("/{event_id}")
def update_event(
    event_id: int,
    request: EventRequest,
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
) -> EventResponse:
    return events_service.update_event(event_id, request, current_agency)
