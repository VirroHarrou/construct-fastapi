from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fio = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, index=True)
    address = Column(String(255))
    inn = Column(String(12), unique=True, index=True)
    image_url = Column(String(511))
    orders = relationship(
        "Order", 
        back_populates="owner",
        cascade="all, delete-orphan", 
        passive_deletes=True
    )
    viewed_orders = relationship(
        "Order", 
        secondary="order_views",
        back_populates="viewers"
    )
    company_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("companies.id"), 
        nullable=True
    )
    company = relationship("Company", back_populates="user")
    sent_reviews = relationship( 
        "Review", 
        foreign_keys="[Review.sender_id]",
        back_populates="sender",
        cascade="all, delete",
        passive_deletes=True
    )
    received_reviews = relationship( 
        "Review", 
        foreign_keys="[Review.recipient_id]",
        back_populates="recipient",
        cascade="all, delete",
        passive_deletes=True
    )