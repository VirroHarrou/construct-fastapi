from fastapi import APIRouter, Depends
from uuid import UUID
from app.schemas.review import ReviewCreate, ReviewResponse
from app.schemas.users import UserResponse
from app.services.review import ReviewService
from app.dependencies.database import get_db
from app.dependencies.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["reviews"])

def get_review_service(session: AsyncSession = Depends(get_db)) -> ReviewService:
    return ReviewService(session)

@router.post("/reviews/", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    user: UserResponse = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    return await service.create_review(user.id, review_data)

@router.get("/orders/{order_id}/reviews", response_model=list[ReviewResponse])
async def get_order_reviews(
    order_id: UUID,
    service: ReviewService = Depends(get_review_service),
):
    return await service.get_reviews_by_order(order_id)

@router.delete("/reviews/{review_id}", status_code=204)
async def delete_review(
    review_id: UUID,
    user: UserResponse = Depends(get_current_user),
    service: ReviewService = Depends(get_review_service),
):
    await service.delete_review(user.id, review_id)