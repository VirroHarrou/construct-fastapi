import uuid
from sqlalchemy import Column, UUID, ForeignKey, Text, Integer, DateTime
from sqlalchemy.orm import relationship
from app.models.base import Base
from datetime import datetime, timezone

class Review(Base):
    __tablename__ = "reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))

    # Relationships
    user = relationship("User", back_populates="reviews")
    order = relationship("Order", back_populates="reviews")