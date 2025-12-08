from pydantic import BaseModel


class HealthResponse(BaseModel):
    health: str = "OK"
