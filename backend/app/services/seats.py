from typing import Annotated

from app.db.models import Event, EventSeat, Ticket, TicketStatus
from app.db.session import DBSession
from app.dto.seats import SeatPricing, SeatResponse, SeatsResponse, SeatsSummary
from app.util.seat_format import format_seat_label
from fastapi import Depends, HTTPException, status
from sqlmodel import select


class SeatService:
    def __init__(self, db: DBSession):
        self.db = db

    def get_event_seats(self, event_id: int) -> SeatsResponse:
        event = self.db.exec(select(Event).where(Event.id == event_id)).first()

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        seats = self.db.exec(
            select(EventSeat).where(EventSeat.event_id == event_id)
        ).all()

        booked_seat_numbers = set(
            self.db.exec(
                select(Ticket.seat_number)
                .where(Ticket.event_id == event_id)
                .where(Ticket.status == TicketStatus.CONFIRMED)
            ).all()
        )

        seat_responses = [
            SeatResponse(
                seat_number=seat.seat_number,
                seat_label=format_seat_label(seat.seat_number),
                seat_type=seat.seat_type,
                is_available=seat.seat_number not in booked_seat_numbers,
            )
            for seat in seats
        ]

        return SeatsResponse(
            seats=seat_responses,
            pricing=SeatPricing(
                vip=event.vip_ticket_price,
                regular=event.ticket_price,
            ),
            summary=SeatsSummary(
                total_seats=len(seats),
                available_seats=len(seats) - len(booked_seat_numbers),
            ),
        )


def get_seat_service(db: DBSession):
    return SeatService(db)


SeatServiceDep = Annotated[SeatService, Depends(get_seat_service)]
