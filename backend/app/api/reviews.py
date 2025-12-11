from app.dto.pagination import PaginationParams
from app.dto.reviews import ReviewCreateRequest, ReviewResponse
from app.services.auth import CurrentUser
from app.services.reviews import ReviewServiceDep
from fastapi import APIRouter, status
from fastapi_pagination import Page

router = APIRouter()


@router.get(
    "/reviews/{review_id}",
    description="Get details of a specific review by its ID",
)
def get_review(
    review_id: int,
    reviews_service: ReviewServiceDep,
) -> ReviewResponse:
    return reviews_service.get_review(review_id)


@router.post(
    "/tickets/{ticket_id}/review",
    status_code=status.HTTP_201_CREATED,
    description="Create a review for a ticket after event starts",
)
def create_review(
    ticket_id: int,
    request: ReviewCreateRequest,
    current_user: CurrentUser,
    reviews_service: ReviewServiceDep,
) -> ReviewResponse:
    return reviews_service.create_review(current_user, ticket_id, request)


@router.get(
    "/events/{event_id}/reviews",
    description="List all reviews for an event with pagination",
)
def list_event_reviews(
    event_id: int,
    params: PaginationParams,
    reviews_service: ReviewServiceDep,
) -> Page[ReviewResponse]:
    return reviews_service.list_event_reviews(event_id, params)


@router.put(
    "/reviews/{review_id}",
    description="Update your own review",
)
def update_review(
    review_id: int,
    request: ReviewCreateRequest,
    current_user: CurrentUser,
    reviews_service: ReviewServiceDep,
) -> ReviewResponse:
    return reviews_service.update_review(review_id, current_user, request)


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete your own review",
)
def delete_review(
    review_id: int,
    current_user: CurrentUser,
    reviews_service: ReviewServiceDep,
):
    return reviews_service.delete_review(review_id, current_user)
