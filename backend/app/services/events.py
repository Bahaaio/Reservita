from datetime import datetime
from typing import Annotated
from uuid import UUID

from app.core.config import settings
from app.db.models import (
    Event,
    EventBanner,
    EventSeat,
    FavoriteEvent,
    Review,
    SeatType,
    User,
)
from app.db.session import DBSession
from app.dto.events import BannerResponse, EventRequest, EventResponse
from app.util.files import (
    delete_file,
    get_banner_path,
    get_image_response,
    save_file,
    validate_image_file,
)
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from fastapi_pagination import Page, Params, create_page
from sqlmodel import func, select

# FIX: n+1


class EventService:
    def __init__(self, db: DBSession):
        self.db = db

    def get_event(
        self, event_id: int, current_user: User | None = None
    ) -> EventResponse:
        db_event = self.db.get(Event, event_id)

        if not db_event:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        return self._event_to_response(db_event, current_user)

    def list_all_events(
        self, params: Params, current_user: User | None = None
    ) -> Page[EventResponse]:
        total = self.db.exec(select(func.count()).select_from(Event)).one()
        offset = (params.page - 1) * params.size

        db_events = self.db.exec(select(Event).offset(offset).limit(params.size)).all()

        # FIX: n+1
        events: list[EventResponse] = [
            self._event_to_response(event, current_user) for event in db_events
        ]

        return create_page(events, total, params)

    def list_agency_events(self, params: Params, agency: User) -> Page[EventResponse]:
        total = self.db.exec(
            select(func.count()).select_from(Event).where(Event.creator_id == agency.id)
        ).one()
        offset = (params.page - 1) * params.size

        db_events = self.db.exec(
            select(Event)
            .where(Event.creator_id == agency.id)
            .offset(offset)
            .limit(params.size)
        ).all()

        events: list[EventResponse] = [
            self._event_to_response(event, agency) for event in db_events
        ]

        return create_page(events, total, params)

    def create_event(self, agency: User, request: EventRequest) -> EventResponse:
        if request.starts_at <= datetime.now():
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Event start time must be in the future",
            )

        if request.starts_at >= request.ends_at:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Event start time must be before end time",
            )

        event = Event(**request.model_dump())
        event.creator = agency

        self.db.add(event)
        self.db.flush()
        self.db.refresh(event)

        assert event.id is not None

        # TODO: change hardcoded 100 seats (10 vip + 90 regular)

        vip_seats: list[EventSeat] = [
            EventSeat(event_id=event.id, seat_number=i + 1, seat_type=SeatType.VIP)
            for i in range(10)
        ]

        regular_seats: list[EventSeat] = [
            EventSeat(event_id=event.id, seat_number=i + 1, seat_type=SeatType.REGULAR)
            for i in range(10, 100)
        ]

        self.db.add_all(vip_seats)
        self.db.add_all(regular_seats)
        self.db.commit()

        return self._event_to_response(event)

    def update_event(
        self, event_id: int, request: EventRequest, agency: User
    ) -> EventResponse:
        event = self.db.exec(select(Event).where(Event.id == event_id)).first()

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND)

        if event.creator_id != agency.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

        event.sqlmodel_update(request.model_dump(exclude_unset=True))

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return self._event_to_response(event)

    def get_banner(self, banner_id: UUID) -> FileResponse:
        banner = self.db.get(EventBanner, banner_id)

        if not banner:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Banner not found")

        return get_image_response(get_banner_path(banner_id))

    def upload_banner(
        self, event_id: int, file: UploadFile, agency: User
    ) -> BannerResponse:
        event = self.db.get(Event, event_id)

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        if event.creator_id != agency.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")

        if len(event.banners) == settings.MAX_BANNERS_PER_EVENT:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Banner limit reached")

        banner = EventBanner(event_id=event_id)

        validate_image_file(file, settings.MAX_BANNER_SIZE_MB)
        save_file(file, get_banner_path(banner.id))

        self.db.add(banner)
        self.db.commit()

        return BannerResponse(id=banner.id)

    def delete_banner(self, event_id: int, banner_id: UUID, agency: User):
        event = self.db.get(Event, event_id)

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        if event.creator_id != agency.id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Not authorized")

        banner = self.db.get(EventBanner, banner_id)

        if not banner:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Banner not found")

        if banner.event_id != event_id:
            # return 404 to avoid info leak
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Banner not found")

        delete_file(get_banner_path(banner_id))

        self.db.delete(banner)
        self.db.commit()

    def _event_to_response(
        self,
        event: Event,
        current_user: User | None = None,
    ) -> EventResponse:
        is_favorited = False

        if current_user:
            fav_result = self.db.exec(
                select(FavoriteEvent)
                .where(FavoriteEvent.event_id == event.id)
                .where(FavoriteEvent.user_id == current_user.id)
            ).first()

            is_favorited = fav_result is not None

        return EventResponse(
            banner_ids=[banner.id for banner in event.banners],
            average_rating=self._calculate_average_rating(event),
            is_favorited=is_favorited,
            **event.model_dump(),
        )

    def _calculate_average_rating(self, event: Event) -> float:
        avg_rating_result = self.db.exec(
            select(func.avg(Review.rating)).where(Review.event_id == event.id)
        ).first()

        return float(avg_rating_result) if avg_rating_result else 0.0


def get_event_service(db: DBSession) -> EventService:
    return EventService(db)


EventServiceDep = Annotated[EventService, Depends(get_event_service)]
