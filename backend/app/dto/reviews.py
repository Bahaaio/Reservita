from pydantic import BaseModel, Field
from datetime import datetime

class ReviewCreateRequest(BaseModel):
    rating: float = Field(...,ge=1,le=5)
    comment: str | None = Field(
        default=None,
        min_length=10,
        max_length=1000,
    )

class ReviewResponse(BaseModel):
    id: int
    user_full_name: str
    rating: float
    comment: str | None
    created_at: datetime

    class Config:
        from_attributes = True


