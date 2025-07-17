from pydantic import UUID4, BaseModel, ConfigDict, Field
from datetime import datetime

class ReviewBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=512)
    rating: int = Field(..., ge=1, le=5)
    recipient_id: UUID4

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: UUID4
    sender_id: UUID4
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)