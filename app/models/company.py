import uuid
from sqlalchemy import UUID, Column, String
from sqlalchemy.orm import relationship
from app.models.base import Base

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    user_id = Column(UUID, ForeignKey("users.id")) 
    
    # Обратная связь один-к-одному
    user = relationship("User", back_populates="company", uselist=False)
