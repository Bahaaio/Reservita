from datetime import datetime
from pydantic import BaseModel

from app.db.models import EventCategory


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
    banner_uuids: list[str]

    average_rating: float
    is_favorited: bool  # if authenticated user has favorited this event

    class Config:
        from_attributes = True
