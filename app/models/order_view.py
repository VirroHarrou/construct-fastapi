from sqlalchemy import Column, ForeignKey, Index, SmallInteger, String
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base


class OrderView(Base):
    __tablename__ = "order_views"
    __table_args__ = (
        Index('ix_order_views_order_id', 'order_id'),
    )
    
    user_id = Column(UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    order_id = Column(UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False
    )
    status = Column(SmallInteger, nullable=True, default=None)