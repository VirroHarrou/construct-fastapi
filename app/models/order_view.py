from sqlalchemy import Column, ForeignKey, Index, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class OrderView(Base):
    __tablename__ = "order_views"
    __table_args__ = (
        Index('ix_order_views_order_id', 'order_id'),
    )
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), primary_key=True)
    status = Column(SmallInteger)