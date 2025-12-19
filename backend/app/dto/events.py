from datetime import datetime
from typing import Annotated
from uuid import UUID

from app.db.models import EventCategory
from fastapi import Depends, Query
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator
from typing_extensions import Self


class EventFilterParams(BaseModel):
    # Search keyword (e.g. ?q=concert)
    q: str | None = None

    # Filter by Category (e.g. ?category=sports&category=comedy)
    category: list[EventCategory] | None = None

    # Filter by City
    city: str | None = None

    # Date Range
    start_date: datetime | None = None
    end_date: datetime | None = None

    # Price Filters
    min_price: float | None = None
    max_price: float | None = None
    is_free: bool | None = None

    @field_validator("start_date", "end_date", mode="after")
    @classmethod
    def strip_timezone(cls, v: datetime | None):
        if v:
            return v.replace(tzinfo=None)
        return v

    @field_validator("q", "city")
    @classmethod
    def validate_not_blank(cls, v: str | None, info) -> str | None:
        if v is not None:
            stripped = v.strip()
            if stripped == "":
                raise ValueError(f"{info.field_name} cannot be blank")
            return stripped
        return v

    @model_validator(mode="after")
    def validate_filters(self) -> Self:
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValueError("start_date must be before end_date")

        if self.is_free is True and (
            self.min_price is not None or self.max_price is not None
        ):
            raise ValueError(
                "Cannot specify price filters when filtering for free events"
            )

        if self.min_price and self.max_price and self.min_price > self.max_price:
            raise ValueError("min_price cannot be greater than max_price")

        return self


def get_event_filters(
    q: str | None = None,
    category: list[EventCategory] | None = None,
    city: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    is_free: bool | None = None,
) -> EventFilterParams:
    try:
        return EventFilterParams(
            q=q,
            category=category if category else None,
            city=city,
            start_date=start_date,
            end_date=end_date,
            min_price=min_price,
            max_price=max_price,
            is_free=is_free,
        )
    except ValidationError as e:
        raise RequestValidationError(errors=e.errors())


FilterParams = Annotated[EventFilterParams, Depends(get_event_filters)]


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
    total_seats: int = Field(ge=1)
    vip_seats_count: int = Field(ge=0)

    @field_validator("starts_at", "ends_at", mode="after")
    @classmethod
    def strip_timezone(cls, v: datetime):
        """Remove timezone info from incoming datetimes."""
        return v.replace(tzinfo=None)


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
    total_seats: int
    vip_seats_count: int

    average_rating: float
    is_favorited: bool  # if authenticated user has favorited this event

    class Config:
        from_attributes = True


class BannerResponse(BaseModel):
    id: UUID
