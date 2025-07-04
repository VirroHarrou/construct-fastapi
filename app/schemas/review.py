from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from uuid import UUID

class ReviewBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=512)
    rating: int = Field(..., ge=1, le=5)
    recepient_id: UUID

class ReviewCreate(ReviewBase):
    pass

class ReviewResponse(ReviewBase):
    id: UUID
    sender_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)