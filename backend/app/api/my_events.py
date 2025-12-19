from uuid import UUID

from app.dto.analytics import AgencyAnalyticsResponse, AgencyEventAnalyticsResponse
from app.dto.events import BannerResponse, EventRequest, EventResponse
from app.dto.pagination import PaginationParams
from app.services.auth import CurrentAgency
from app.services.events import EventServiceDep
from fastapi import APIRouter, UploadFile, status
from fastapi_pagination import Page

router = APIRouter(prefix="/my-events", tags=["Agency Events"])


@router.get("", description="List events for the current agency with pagination")
def list_my_events(
    params: PaginationParams,
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
) -> Page[EventResponse]:
    return events_service.list_agency_events(params, current_agency)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Create a new event for the current agency",
)
def create_event(
    request: EventRequest,
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
) -> EventResponse:
    return events_service.create_event(current_agency, request)


@router.put(
    "/{event_id}", description="Update an existing event for the current agency"
)
def update_event(
    event_id: int,
    request: EventRequest,
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
) -> EventResponse:
    return events_service.update_event(event_id, request, current_agency)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete an existing event for the current agency",
)
def delete_event(
    event_id: int,
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
):
    events_service.delete_event(event_id, current_agency)


@router.post(
    "/{event_id}/banners",
    status_code=status.HTTP_201_CREATED,
    description="Upload a banner for an existing event",
)
def upload_banner(
    event_id: int,
    file: UploadFile,
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
) -> BannerResponse:
    return events_service.upload_banner(event_id, file, current_agency)


@router.delete(
    "/{event_id}/banners/{banner_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete a banner from an existing event",
)
def delete_banner(
    event_id: int,
    banner_id: UUID,
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
):
    events_service.delete_banner(event_id, banner_id, current_agency)


@router.get(
    "/analytics",
    description="Get analytics for the current agency",
)
def get_agency_analytics(
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
) -> AgencyAnalyticsResponse:
    return events_service.get_agency_analytics(current_agency)


@router.get(
    "/analytics/events",
    description="List analytics for each event of the current agency",
)
def list_agency_events_analytics(
    current_agency: CurrentAgency,
    events_service: EventServiceDep,
) -> list[AgencyEventAnalyticsResponse]:
    return events_service.list_agency_events_analytics(current_agency)
