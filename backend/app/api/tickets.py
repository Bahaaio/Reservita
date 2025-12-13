from fastapi import APIRouter, Response
from fastapi.responses import StreamingResponse

from app.dto.tickets import TicketBookRequest, TicketResponse
from app.services.auth import CurrentUser
from app.services.tickets import TicketServiceDep

router = APIRouter(prefix="/tickets", tags=["Tickets"])

@router.post("", description="Book a new ticket")
def book_ticket(
    request: TicketBookRequest,
    current_user: CurrentUser,
    ticket_service: TicketServiceDep,
) -> TicketResponse:
    return ticket_service.book_ticket(current_user, request)

@router.get("", description="List all tickets belonging to the current user")
def list_my_tickets(
    current_user: CurrentUser,
    ticket_service: TicketServiceDep,
) -> list[TicketResponse]:
    return ticket_service.list_my_tickets(current_user)

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
) -> TicketResponse:
    return ticket_service.cancel_ticket(ticket_id, current_user)

@router.get(
    "/{ticket_id}/qr", 
    description="Get the QR code as a PNG image",
    response_class=StreamingResponse 
)
def get_ticket_qr(
    ticket_id: int,
    current_user: CurrentUser,
    ticket_service: TicketServiceDep,
) -> StreamingResponse:
    return ticket_service.get_ticket_qr(ticket_id, current_user)