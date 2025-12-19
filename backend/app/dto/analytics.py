from pydantic import BaseModel


class AgencyAnalyticsResponse(BaseModel):
    """Aggregated analytics for all agency events."""

    total_events: int
    total_tickets_sold: int
    total_revenue: float


class AgencyEventAnalyticsResponse(BaseModel):
    """Analytics for a specific event."""

    event_id: int
    tickets_sold: int
    revenue: float
