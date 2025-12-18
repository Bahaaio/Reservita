from app.dto.tickets import (
    QRCodeVerificationRequest,
    QRCodeVerificationResponse,
    TicketBookRequest,
    TicketResponse,
)
from app.services.auth import CurrentUser
from app.services.tickets import TicketServiceDep
from fastapi import APIRouter, BackgroundTasks, status
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("", description="List all tickets belonging to the current user")
def list_my_tickets(
    current_user: CurrentUser,
    ticket_service: TicketServiceDep,
) -> list[TicketResponse]:
    return ticket_service.list_my_tickets(current_user)


@router.post("", status_code=status.HTTP_201_CREATED, description="Book a new ticket")
def book_ticket(
    request: TicketBookRequest,
    current_user: CurrentUser,
    ticket_service: TicketServiceDep,
    background_tasks: BackgroundTasks,
) -> TicketResponse:
    return ticket_service.book_ticket(current_user, request, background_tasks)


@router.get("/{ticket_id}", description="Get details of a specific ticket")
def get_ticket(
    ticket_id: int,
    current_user: CurrentUser,
    ticket_service: TicketServiceDep,
) -> TicketResponse:
    return ticket_service.get_ticket(ticket_id, current_user)


@router.delete("/{ticket_id}", description="Cancel a ticket")
def cancel_ticket(
    ticket_id: int,
    current_user: CurrentUser,
    ticket_service: TicketServiceDep,
    background_tasks: BackgroundTasks,
) -> TicketResponse:
    return ticket_service.cancel_ticket(ticket_id, current_user, background_tasks)


@router.get(
    "/{ticket_id}/qr",
    description="Get the QR code as a PNG image",
)
def get_ticket_qr(
    ticket_id: int,
    current_user: CurrentUser,
    ticket_service: TicketServiceDep,
) -> StreamingResponse:
    return ticket_service.get_ticket_qr(ticket_id, current_user)


@router.post("/qr/verify", description="Verify a ticket using its QR code")
def verify_ticket_qr(
    request: QRCodeVerificationRequest, ticket_service: TicketServiceDep
) -> QRCodeVerificationResponse:
    return ticket_service.verify_ticket_qr(request)
