import io
import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

import qrcode
from app.db.models import Event, EventSeat, SeatType, Ticket, TicketStatus, User
from app.db.session import DBSession
from app.dto.tickets import TicketBookRequest, TicketResponse
from fastapi import Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import IntegrityError
from sqlmodel import select


class TicketService:
    def __init__(self, db: DBSession):
        self.db = db

    def book_ticket(self, user: User, request: TicketBookRequest) -> TicketResponse:
        event = self.db.get(Event, request.event_id)
        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        if event.starts_at <= datetime.now(timezone.utc):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Cannot book tickets for past or ongoing events",
            )

        seat = self.db.get(EventSeat, (request.event_id, request.seat_number))
        if not seat:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Seat number does not exist")

        existing_ticket = self.db.exec(
            select(Ticket)
            .where(Ticket.event_id == request.event_id)
            .where(Ticket.seat_number == request.seat_number)
            .where(Ticket.status == TicketStatus.CONFIRMED)
        ).first()

        if existing_ticket:
            raise HTTPException(status.HTTP_409_CONFLICT, "This seat is already booked")

        generated_qr = f"TICKET-{request.event_id}-{request.seat_number}-{uuid.uuid4().hex[:6].upper()}"

        assert user.id is not None

        try:
            new_ticket = Ticket(
                user_id=user.id,
                event_id=request.event_id,
                seat_number=request.seat_number,
                qr_code=generated_qr,
                status=TicketStatus.CONFIRMED,
            )

            self.db.add(new_ticket)
            self.db.commit()
            self.db.refresh(new_ticket)

            return self._ticket_to_response(new_ticket, event, seat)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "This seat is already booked")

    def list_my_tickets(self, user: User) -> list[TicketResponse]:
        tickets = self.db.exec(select(Ticket).where(Ticket.user_id == user.id)).all()

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
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket not found")

        event = self.db.get(Event, ticket.event_id)

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        seat = self.db.get(EventSeat, (ticket.event_id, ticket.seat_number))

        if not seat:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Seat information not found")

        return self._ticket_to_response(ticket, event, seat)

    def cancel_ticket(self, ticket_id: int, user: User) -> TicketResponse:
        ticket = self.db.get(Ticket, ticket_id)

        if not ticket or ticket.user_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket not found")

        if ticket.status == TicketStatus.CANCELLED:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Ticket is already cancelled"
            )

        event = self.db.get(Event, ticket.event_id)

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        # 24-Hour Rule
        time_until_event = event.starts_at - datetime.now(timezone.utc)

        if time_until_event < timedelta(hours=24):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Cannot cancel less than 24h before event"
            )

        ticket.status = TicketStatus.CANCELLED
        ticket.cancelled_at = datetime.now(timezone.utc)

        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)

        seat = self.db.get(EventSeat, (ticket.event_id, ticket.seat_number))

        if not seat:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Seat information not found")

        return self._ticket_to_response(ticket, event, seat)

    def get_ticket_qr(self, ticket_id: int, user: User) -> StreamingResponse:
        """
        Generates QR in memory (RAM) and returns a StreamingResponse.
        """
        ticket = self.db.get(Ticket, ticket_id)

        if not ticket or ticket.user_id != user.id:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket not found")

        if not ticket.qr_code:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Ticket QR code is invalid"
            )

        qr = qrcode.QRCode(box_size=10, border=4)
        qr.add_data(ticket.qr_code)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf)
        buf.seek(0)

        return StreamingResponse(
            buf,
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=qr.png"},
        )

    def _ticket_to_response(
        self, ticket: Ticket, event: Event, seat: EventSeat
    ) -> TicketResponse:
        """
        Helper to format the output DTO.
        """
        price = (
            event.vip_ticket_price
            if seat.seat_type == SeatType.VIP
            else event.ticket_price
        )

        assert ticket.id is not None

        return TicketResponse(
            id=ticket.id,
            status=ticket.status,
            purchased_at=ticket.purchased_at,
            seat_number=ticket.seat_number,
            seat_type=seat.seat_type,
            price_paid=price,
        )


# Dependency Injection Setup
def get_ticket_service(db: DBSession) -> TicketService:
    return TicketService(db)


TicketServiceDep = Annotated[TicketService, Depends(get_ticket_service)]
