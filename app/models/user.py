from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fio = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, index=True)
    address = Column(String(255))
    inn = Column(String(12), unique=True, index=True)
    orders = relationship("Order", back_populates="owner")
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
    reviews = relationship("Review", back_populates="user")