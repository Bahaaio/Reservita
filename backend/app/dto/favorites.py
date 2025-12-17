from pydantic import BaseModel, Field


class FavoriteRequest(BaseModel):
    event_id: int = Field(ge=1)
