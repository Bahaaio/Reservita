from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship


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
    is_agency: bool

    # Relationships
    created_events: list["Event"] = Relationship(back_populates="creator")
    bookings: list["Booking"] = Relationship(back_populates="user")
    reviews: list["Review"] = Relationship(back_populates="user")
    favorite_events: list["Event"] = Relationship(link_model=FavoriteEvent)


class Seat(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_vip: bool


# Junction Table
class EventSeat(SQLModel, table=True):
    event_id: int | None = Field(default=None, foreign_key="event.id", primary_key=True)
    seat_id: int | None = Field(default=None, foreign_key="seat.id", primary_key=True)
    is_available: bool = True


class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(nullable=False, index=True)
    description: str
    location: str = Field(index=True)
    date: datetime = Field(index=True)
    ticket_price: float
    vip_ticket_price: float
    created_by: int = Field(foreign_key="user.id")

    # Relationships
    creator: User = Relationship(back_populates="created_events")
    seats: list["Seat"] = Relationship(back_populates="events", link_model=EventSeat)
    reviews: list["Review"] = Relationship(back_populates="event")


class Booking(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")
    seat_id: int = Field(foreign_key="seat.id")
    purchase_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    user: User = Relationship(back_populates="bookings")
    event: Event = Relationship(back_populates="bookings")
    seat: Seat = Relationship(back_populates="bookings")
    review: Optional["Review"] = Relationship(back_populates="booking")


class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    booking_id: int = Field(foreign_key="booking.id", unique=True)
    user_id: int = Field(foreign_key="user.id")
    event_id: int = Field(foreign_key="event.id")
    rating: int = Field(nullable=False, ge=1, le=5)
    comment: str
    review_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationships
    booking: Booking = Relationship(back_populates="review")
    user: User = Relationship(back_populates="reviews")
    event: Event = Relationship(back_populates="reviews")
