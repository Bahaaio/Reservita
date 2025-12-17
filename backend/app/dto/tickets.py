from datetime import datetime

from app.db.models import SeatType, TicketStatus
from pydantic import BaseModel


class TicketBookRequest(BaseModel):
    """
    Validation schema for booking a new ticket.
    """

    event_id: int
    seat_number: int


class TicketResponse(BaseModel):
    """
    The ticket details sent back to the frontend.
    """

    id: int
    event_id: int
    status: TicketStatus
    purchased_at: datetime
    seat_number: int
    seat_type: SeatType
    price_paid: float


class QRCodeVerificationRequest(BaseModel):
    """
    Validation schema for verifying a ticket QR code.
    """

    qr_token: str


class QRCodeVerificationResponse(BaseModel):
    """
    The response sent back after verifying a ticket QR code.
    """

    valid: bool
    ticket: TicketResponse | None = None
