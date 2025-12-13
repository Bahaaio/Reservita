from datetime import datetime
from pydantic import BaseModel
from app.db.models import TicketStatus, SeatType

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
    status: TicketStatus
    purchased_at: datetime
    seat_number: int
    seat_type: SeatType
    price_paid: float