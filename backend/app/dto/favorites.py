from pydantic import BaseModel

class FavoriteRequest(BaseModel):
    event_id: int

