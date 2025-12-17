from typing import Annotated

from app.db.models import Event, FavoriteEvent, User
from app.db.session import DBSession
from app.dto.favorites import FavoriteRequest
from fastapi import Depends, HTTPException, status
from sqlmodel import select


class FavoriteService:
    def __init__(self, db: DBSession):
        self.db = db

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

    def remove_from_favorites(self, user: User, request: FavoriteRequest):
        event = self.db.get(Event, request.event_id)

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        favorite = self.db.exec(
            select(FavoriteEvent)
            .where(FavoriteEvent.user_id == user.id)
            .where(FavoriteEvent.event_id == request.event_id)
        ).first()

        if not favorite:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Favorite not found")

        self.db.delete(favorite)
        self.db.commit()


def get_favorite_service(db: DBSession) -> FavoriteService:
    return FavoriteService(db)


FavoriteServiceDep = Annotated[FavoriteService, Depends(get_favorite_service)]
