from app.db.models import SeatType
from pydantic import BaseModel


class SeatResponse(BaseModel):
    seat_number: int
    seat_label: str
    seat_type: SeatType
    is_available: bool

    class Config:
        from_attributes = True


class SeatPricing(BaseModel):
    vip: float
    regular: float


class SeatsSummary(BaseModel):
    total_seats: int
    available_seats: int


class SeatsResponse(BaseModel):
    seats: list[SeatResponse]
    pricing: SeatPricing
    summary: SeatsSummary
