from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class SeatType(str, Enum):
    REGULAR = "regular"
    VIP = "vip"


class EventCategory(str, Enum):
    SPORTS = "sports"
    THEATER = "theater"
    CONFERENCE = "conference"
    COMEDY = "comedy"
    OTHER = "other"


class FavoriteEvent(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    event_id: int | None = Field(default=None, foreign_key="event.id", primary_key=True)


# Main Tables
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    full_name: str = Field(nullable=False)
    email: str = Field(index=True, unique=True)
    hashed_password: str = Field(nullable=False)
    phone_number: str
    is_agency: bool = Field(default=False)

    # Relationships
    created_events: list["Event"] = Relationship(back_populates="creator")
    tickets: list["Ticket"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")
    favorite_events: list["Event"] = Relationship(link_model=FavoriteEvent)


class EventBanner(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_id: int = Field(foreign_key="event.id")
    uuid: str = Field(nullable=False)

    # Relationships
    event: "Event" = Relationship(back_populates="banners")


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, index=True)
    description: str
    category: EventCategory = Field(default=EventCategory.OTHER, index=True)
    city: str = Field(index=True, nullable=False)
    venue: str = Field(nullable=False)
    address: str = Field(nullable=False)
    starts_at: datetime = Field(index=True)
    ends_at: datetime = Field(index=True)
    # TODO: change
    ticket_price: float = Field(ge=0)
    vip_ticket_price: float = Field(ge=0)
    creator_id: int = Field(foreign_key="user.id")

    # Relationships
    creator: User = Relationship(back_populates="created_events")
    event_seats: list["EventSeat"] = Relationship(back_populates="event")
    tickets: list["Ticket"] = Relationship(back_populates="event")
    reviews: list["Review"] = Relationship(back_populates="event")
    banners: list["EventBanner"] = Relationship(back_populates="event")


class EventSeat(SQLModel, table=True):
    event_id: int = Field(foreign_key="event.id", primary_key=True)
    seat_number: int = Field(primary_key=True)
    seat_type: SeatType = Field(default=SeatType.REGULAR)

    # Relationships
    event: "Event" = Relationship(back_populates="event_seats")


class TicketStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Ticket(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")
    seat_number: int
    qr_code: str = Field(
        nullable=False, unique=True, index=True
    )  # "TICKET-XXXX" # TODO: make jwt
    status: TicketStatus = Field(
        default=TicketStatus.CONFIRMED, nullable=False, index=True
    )
    purchased_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    cancelled_at: datetime | None = Field(default=None)

    # Composite foreign key to EventSeat
    __table_args__ = (
        ForeignKeyConstraint(
            ["event_id", "seat_number"],
            ["eventseat.event_id", "eventseat.seat_number"],
            name="fk_ticket_event_seat",
        ),
        # Unique constraint: one ticket per seat
        UniqueConstraint("event_id", "seat_number", name="unique_event_seat_ticket"),
    )

    # Relationships
    user: User = Relationship(back_populates="tickets")
    event: Event = Relationship(back_populates="tickets")
    event_seat: Optional[EventSeat] = Relationship(
        sa_relationship_kwargs={"viewonly": True}
    )
    review: Optional["Review"] = Relationship(back_populates="ticket")


class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id", unique=True)
    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")
    rating: float = Field(nullable=False, ge=1, le=5)
    comment: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    ticket: Ticket = Relationship(back_populates="review")
    user: User = Relationship(back_populates="reviews")
    event: Event = Relationship(back_populates="reviews")
