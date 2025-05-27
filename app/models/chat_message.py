import uuid
from sqlalchemy import UUID, Boolean, Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.models.base import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message = Column(String(512))
    created_at = Column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))
    updated_at = Column(DateTime, nullable=True)
    is_edited = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])