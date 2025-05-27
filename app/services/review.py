from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewResponse

class ReviewService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_review(self, user_id: UUID, data: ReviewCreate) -> ReviewResponse:
        review = Review(
            user_id=user_id,
            order_id=data.order_id,
            text=data.text,
            rating=data.rating
        )
        self.session.add(review)
        await self.session.commit()
        return review

    async def get_reviews_by_order(self, order_id: UUID) -> list[ReviewResponse]:
        result = await self.session.execute(
            select(Review)
            .filter(Review.order_id == order_id)
        )
        reviews = result.scalars().all()
        return [ReviewResponse.model_validate(o) for o in reviews]

    async def delete_review(self, user_id: UUID, review_id: UUID):
        review = await self.session.get(Review, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found"
                )
        if user_id != review.user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed",
                )
        
        await self.session.delete(review)
        await self.session.commit()