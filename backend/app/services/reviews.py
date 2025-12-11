from typing import Annotated
from datetime import datetime, timezone
from app.db.models import Review, Ticket, Event, User
from app.db.session import DBSession
from app.dto.reviews import ReviewCreateRequest, ReviewResponse, DeleteResponse
from app.dto.pagination import PaginationParams
from fastapi import Depends, HTTPException, status
from fastapi_pagination import Page, Params, create_page
from sqlmodel import func, select


class ReviewService:
    def __init__(self, db: DBSession):
        self.db = db

    def create_review(
            self,
            user: User,
            ticket_id: int,
            request: ReviewCreateRequest,
    ) -> ReviewResponse:
        ticket = self.db.exec(
            select(Ticket).where(Ticket.id == ticket_id)
        ).first()

        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found",
            )
        
        if ticket.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review your own tickets",
            )
        
        event = ticket.event

        if event.starts_at > datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot review an event that has not started yet",
            )
        
        existing_review = self.db.exec(
            select(Review).where(Review.ticket_id == ticket_id)
        ).first()

        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review for this ticket already exists",
            )
        
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
        review = self.db.exec(
            select(Review).where(Review.id == review_id)
        ).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        return self._review_to_response(review)

    def list_event_reviews(
            self,
            event_id: int,
            params: PaginationParams,
    ) -> Page[ReviewResponse]:
        event = self.db.exec(
            select(Event).where(Event.id == event_id)
        ).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found",
            )
        
        total = self.db.exec(
            select(func.count()).select_from(Review).where(Review.event_id == event_id)
        ).one()

        offset = (params.page - 1) * params.size

        reviews = self.db.exec(
            select(Review)
            .where(Review.event_id == event_id)
            .order_by(Review.created_at.desc())
            .offset(offset)
            .limit(params.size)
        ).all()
        
        responses = [self._review_to_response(review) for review in reviews]
        
        return create_page(responses, total, params)

    def update_review(
            self,
            review_id: int,
            user: User,
            request: ReviewCreateRequest,
    ) -> ReviewResponse:
        review = self.db.exec(
            select(Review).where(Review.id == review_id)
        ).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        
        if review.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reviews",
            )

        review.rating = request.rating
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
        review = self.db.exec(
            select(Review).where(Review.id == review_id)
        ).first()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        
        if review.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews",
            )
        
        self.db.delete(review)
        self.db.commit()

    def _review_to_response(self, review: Review) -> ReviewResponse:
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