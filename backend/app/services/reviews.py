from datetime import datetime, timezone
from typing import Annotated

from app.db.models import Event, Review, Ticket, User
from app.db.session import DBSession
from app.dto.pagination import PaginationParams
from app.dto.reviews import ReviewCreateRequest, ReviewResponse, ReviewUpdateRequest
from fastapi import Depends, HTTPException, status
from fastapi_pagination import Page, create_page
from sqlmodel import desc, func, select


class ReviewService:
    def __init__(self, db: DBSession):
        self.db = db

    def create_review(
        self,
        user: User,
        ticket_id: int,
        request: ReviewCreateRequest,
    ) -> ReviewResponse:
        ticket = self.db.exec(select(Ticket).where(Ticket.id == ticket_id)).first()

        if not ticket:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Ticket not found")

        if ticket.user_id != user.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "You can only review your own tickets"
            )

        event = ticket.event

        if event.starts_at > datetime.now(timezone.utc):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Cannot review an event that has not started yet",
            )

        existing_review = self.db.exec(
            select(Review).where(Review.ticket_id == ticket_id)
        ).first()

        if existing_review:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Review for this ticket already exists"
            )

        assert user.id is not None
        assert event.id is not None

        review = Review(
            ticket_id=ticket_id,
            user_id=user.id,
            event_id=event.id,
            rating=request.rating,
            comment=request.comment,
        )

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        return self._review_to_response(review)

    def get_review(self, review_id: int) -> ReviewResponse:
        review = self.db.exec(select(Review).where(Review.id == review_id)).first()

        if not review:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")

        return self._review_to_response(review)

    def list_event_reviews(
        self,
        event_id: int,
        params: PaginationParams,
    ) -> Page[ReviewResponse]:
        event = self.db.exec(select(Event).where(Event.id == event_id)).first()

        if not event:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Event not found")

        total = self.db.exec(
            select(func.count()).select_from(Review).where(Review.event_id == event_id)
        ).one()

        offset = (params.page - 1) * params.size

        reviews = self.db.exec(
            select(Review)
            .where(Review.event_id == event_id)
            .offset(offset)
            .limit(params.size)
            .order_by(desc(Review.created_at))
        ).all()

        responses = [self._review_to_response(review) for review in reviews]

        return create_page(responses, total, params)

    def update_review(
        self,
        review_id: int,
        user: User,
        request: ReviewUpdateRequest,
    ) -> ReviewResponse:
        review = self.db.exec(select(Review).where(Review.id == review_id)).first()

        if not review:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")

        if review.user_id != user.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "You can only update your own reviews"
            )

        if request.rating:
            review.rating = request.rating

        if request.comment:
            review.comment = request.comment

        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)

        return self._review_to_response(review)

    def delete_review(
        self,
        review_id: int,
        user: User,
    ):
        review = self.db.exec(select(Review).where(Review.id == review_id)).first()

        if not review:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Review not found")

        if review.user_id != user.id:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "You can only delete your own reviews"
            )

        self.db.delete(review)
        self.db.commit()

    def _review_to_response(self, review: Review) -> ReviewResponse:
        assert review.id is not None

        return ReviewResponse(
            id=review.id,
            user_full_name=review.user.full_name,
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at,
        )


def get_review_service(db: DBSession) -> ReviewService:
    return ReviewService(db)


ReviewServiceDep = Annotated[ReviewService, Depends(get_review_service)]
