from typing import Annotated

from app.db.models import Event, FavoriteEvent, User
from app.db.session import DBSession
from app.dto.events import EventResponse
from app.dto.favorites import FavoriteRequest
from fastapi import Depends, HTTPException, status
from sqlalchemy import delete
from sqlmodel import select


class FavoriteService:
    def __init__(self, db: DBSession):
        self.db = db

    def get_favorites(self, user: User) -> list[EventResponse]:
        favorite_events = user.favorite_events

        from app.services.events import EventService

        # Create a temporary EventService instance to use _event_to_response
        event_service = EventService(self.db)

        # Convert each Event to EventResponse with computed fields
        return [
            event_service._event_to_response(event, user) for event in favorite_events
        ]

    def add_to_favorites(self, user: User, request: FavoriteRequest):
        event = self.db.get(Event, request.event_id)

        if not event:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Event not found")

        existing = self.db.exec(
            select(FavoriteEvent)
            .where(FavoriteEvent.user_id == user.id)
            .where(FavoriteEvent.event_id == request.event_id)
        ).first()

        if existing:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Event already favorited")

        favorite = FavoriteEvent(user_id=user.id, event_id=request.event_id)
        self.db.add(favorite)
        self.db.commit()

    def remove_from_favorites(self, user: User, event_id: int):
        event = self.db.get(Event, event_id)

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        favorite = self.db.exec(
            select(FavoriteEvent)
            .where(FavoriteEvent.user_id == user.id)
            .where(FavoriteEvent.event_id == event_id)
        ).first()

        if not favorite:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorite not found")

        self.db.delete(favorite)
        self.db.commit()

    def remove_all_favorites(self, user: User):
        self.db.exec(delete(FavoriteEvent).where(FavoriteEvent.user_id == user.id))  # type:ignore[call-overload]
        self.db.commit()


def get_favorite_service(db: DBSession) -> FavoriteService:
    return FavoriteService(db)


FavoriteServiceDep = Annotated[FavoriteService, Depends(get_favorite_service)]
