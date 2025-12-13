import io
import uuid
import qrcode
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import select

from app.db.models import Event, EventSeat, Ticket, TicketStatus, User, SeatType
from app.db.session import DBSession
from app.dto.tickets import TicketBookRequest, TicketResponse

class TicketService:
    def __init__(self, db: DBSession):
        self.db = db

    def book_ticket(self, user: User, request: TicketBookRequest) -> TicketResponse:
        # 1. Check Event
        event = self.db.get(Event, request.event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        # 2. Check Seat existence
        seat = self.db.get(EventSeat, (request.event_id, request.seat_number))
        if not seat:
            raise HTTPException(status_code=404, detail="Seat number does not exist")

        # 3. Check Availability
        existing_ticket = self.db.exec(
            select(Ticket)
            .where(Ticket.event_id == request.event_id)
            .where(Ticket.seat_number == request.seat_number)
            .where(Ticket.status == TicketStatus.CONFIRMED)
        ).first()

        if existing_ticket:
            raise HTTPException(status_code=409, detail="This seat is already booked")

        # 4. Generate Unique QR String
        generated_qr = f"TICKET-{request.event_id}-{request.seat_number}-{uuid.uuid4().hex[:6].upper()}"

        # 5. Create Ticket
        new_ticket = Ticket(
            user_id=user.id,
            event_id=request.event_id,
            seat_number=request.seat_number,
            qr_code=generated_qr,
            status=TicketStatus.CONFIRMED
        )

        self.db.add(new_ticket)
        self.db.commit()
        self.db.refresh(new_ticket)

        return self._ticket_to_response(new_ticket, event, seat)

    def list_my_tickets(self, user: User) -> list[TicketResponse]:
        tickets = self.db.exec(
            select(Ticket).where(Ticket.user_id == user.id)
        ).all()

        results = []
        for ticket in tickets:
            event = self.db.get(Event, ticket.event_id)
            seat = self.db.get(EventSeat, (ticket.event_id, ticket.seat_number))
            if event and seat:
                results.append(self._ticket_to_response(ticket, event, seat))
        
        return results

    def get_ticket(self, ticket_id: int, user: User) -> TicketResponse:
        ticket = self.db.get(Ticket, ticket_id)
        if not ticket or ticket.user_id != user.id:
            raise HTTPException(status_code=404, detail="Ticket not found")

        event = self.db.get(Event, ticket.event_id)
        seat = self.db.get(EventSeat, (ticket.event_id, ticket.seat_number))
        
        return self._ticket_to_response(ticket, event, seat)

    def cancel_ticket(self, ticket_id: int, user: User) -> TicketResponse:
        ticket = self.db.get(Ticket, ticket_id)
        
        if not ticket or ticket.user_id != user.id:
            raise HTTPException(status_code=404, detail="Ticket not found")

        if ticket.status == TicketStatus.CANCELLED:
             raise HTTPException(status_code=400, detail="Ticket is already cancelled")

        # 24-Hour Rule
        event = self.db.get(Event, ticket.event_id)
        time_until_event = event.starts_at - datetime.now(timezone.utc)
        
        if time_until_event < timedelta(hours=24):
            raise HTTPException(status_code=400, detail="Cannot cancel less than 24h before event")

        ticket.status = TicketStatus.CANCELLED
        ticket.cancelled_at = datetime.now(timezone.utc)
        
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        
        seat = self.db.get(EventSeat, (ticket.event_id, ticket.seat_number))
        return self._ticket_to_response(ticket, event, seat)

    def get_ticket_qr(self, ticket_id: int, user: User) -> StreamingResponse:
        """
        Generates QR in memory (RAM) and returns a StreamingResponse.
        """
        ticket = self.db.get(Ticket, ticket_id)
        
        if not ticket or ticket.user_id != user.id:
            raise HTTPException(status_code=404, detail="Ticket not found")

        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(ticket.qr_code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        return StreamingResponse(
            buf,
            media_type="image/png",
            headers={
                "Content-Disposition": f"inline; filename=qr.png"
            }
        )

    def _ticket_to_response(self, ticket: Ticket, event: Event, seat: EventSeat) -> TicketResponse:
        """
        Helper to format the output DTO.
        """
        price = event.vip_ticket_price if seat.seat_type == SeatType.VIP else event.ticket_price
        
        return TicketResponse(
            id=ticket.id,
            status=ticket.status,
            purchased_at=ticket.purchased_at,
            seat_number=ticket.seat_number,
            seat_type=seat.seat_type,
            price_paid=price
        )

# Dependency Injection Setup
def get_ticket_service(db: DBSession) -> TicketService:
    return TicketService(db)

TicketServiceDep = Annotated[TicketService, Depends(get_ticket_service)]