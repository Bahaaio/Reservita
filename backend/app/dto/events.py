from datetime import datetime
from uuid import UUID

from app.db.models import EventCategory
from pydantic import BaseModel, field_validator


class EventRequest(BaseModel):
    title: str
    description: str
    category: EventCategory
    city: str
    venue: str
    address: str
    starts_at: datetime
    ends_at: datetime
    ticket_price: float
    vip_ticket_price: float

    @field_validator("starts_at", "ends_at", mode="after")
    @classmethod
    def strip_timezone(cls, v: datetime):
        """Remove timezone info from incoming datetimes."""
        return v.replace(tzinfo=None)

    # TODO: add total vip and total regular options


class EventResponse(BaseModel):
    id: int
    title: str
    description: str
    category: EventCategory
    city: str
    venue: str
    address: str
    starts_at: datetime
    ends_at: datetime
    ticket_price: float
    vip_ticket_price: float
    banner_ids: list[UUID]

    average_rating: float
    is_favorited: bool  # if authenticated user has favorited this event

    class Config:
        from_attributes = True


class BannerResponse(BaseModel):
    id: UUID
