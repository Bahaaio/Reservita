from datetime import datetime, timezone
from typing import Optional
from enum import Enum
from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlmodel import SQLModel, Field, Relationship


class SeatType(str, Enum):
    REGULAR = "regular"
    VIP = "vip"


class FavoriteEvent(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    event_id: int | None = Field(default=None, foreign_key="event.id", primary_key=True)


# Main Tables
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    email: str = Field(index=True, unique=True)
    hashed_password: str = Field(nullable=False)
    phone_number: str
    is_agency: bool = Field(default=False)

    # Relationships
    created_events: list["Event"] = Relationship(back_populates="creator")
    bookings: list["Booking"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")
    favorite_events: list["Event"] = Relationship(link_model=FavoriteEvent)


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, index=True)
    description: str
    location: str = Field(index=True)
    starts_at: datetime = Field(index=True)
    ends_at: datetime = Field(index=True)
    ticket_price: float
    vip_ticket_price: float
    creator_id: int = Field(foreign_key="user.id")
    banner_url: str | None = Field(default=None)

    # Relationships
    creator: User = Relationship(back_populates="created_events")
    event_seats: list["EventSeat"] = Relationship(back_populates="event")
    bookings: list["Booking"] = Relationship(back_populates="event")
    reviews: list["Review"] = Relationship(back_populates="event")


class EventSeat(SQLModel, table=True):
    event_id: int = Field(foreign_key="event.id", primary_key=True)
    seat_number: int = Field(primary_key=True)
    seat_type: SeatType = Field(default=SeatType.REGULAR)

    # Relationships
    event: "Event" = Relationship(back_populates="event_seats")


class Booking(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")
    seat_number: int
    purchased_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Composite foreign key to EventSeat
    __table_args__ = (
        ForeignKeyConstraint(
            ["event_id", "seat_number"],
            ["eventseat.event_id", "eventseat.seat_number"],
            name="fk_booking_event_seat",
        ),
        # Unique constraint: one booking per seat
        UniqueConstraint("event_id", "seat_number", name="unique_booking_seat"),
    )

    # Relationships
    user: User = Relationship(back_populates="bookings")
    event: Event = Relationship(back_populates="bookings")
    event_seat: Optional[EventSeat] = Relationship()
    review: Optional["Review"] = Relationship(back_populates="booking")


class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="booking.id", unique=True)
    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")
    rating: float = Field(nullable=False, ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    booking: Booking = Relationship(back_populates="review")
    user: User = Relationship(back_populates="reviews")
    event: Event = Relationship(back_populates="reviews")
