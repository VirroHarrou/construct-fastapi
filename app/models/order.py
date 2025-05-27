from sqlalchemy import Column, Index, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base

class Order(Base):
    __tablename__ = "orders"
    __table_args__ = (
        Index('ix_orders_user_id', 'user_id'),
        Index('ix_orders_price', 'price'),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    image_url = Column(String(512))
    price = Column(Numeric(10, 2))
    address = Column(String(255), nullable=False)
    begin_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="orders")
    viewers = relationship(
        "User", 
        secondary="order_views",
        back_populates="viewed_orders"
    )
    reviews = relationship("Review", back_populates="order")