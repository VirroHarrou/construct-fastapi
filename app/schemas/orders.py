from datetime import datetime
from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from sqlalchemy.ext.hybrid import hybrid_property

class OrderBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: float = Field(..., gt=0)
    address: str = Field(..., max_length=255)
    begin_time: datetime
    end_time: datetime
    
    @field_validator('image_url')
    def validate_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError("Invalid URL format")
        return v
    
    @field_validator('begin_time', 'end_time')
    def check_naive_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            raise ValueError("Datetime with timezone is not allowed")
        return value

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: UUID4
    user_id: UUID4
    # viewers
    
    # @hybrid_property
    # def viewers_count(self):
    #     return len(self.viewers)

    model_config = ConfigDict(from_attributes=True)

class OrderUpdate(OrderBase):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    address: Optional[str] = Field(None, max_length=255)
    begin_time: Optional[datetime] = None
    end_time: Optional[datetime] = None