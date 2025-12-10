from app.db.models import SeatType
from pydantic import BaseModel


class SeatResponse(BaseModel):
    seat_number: int
    seat_type: SeatType

    price: float
    is_available: bool

    class Config:
        from_attributes = True


class SeatsResponse(BaseModel):
    seats: list[SeatResponse]
