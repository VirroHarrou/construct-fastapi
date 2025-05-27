from datetime import datetime
from pydantic import UUID4, BaseModel, ConfigDict, Field, HttpUrl, validator
from typing import Optional

class OrderBase(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    price: float = Field(..., gt=0)
    address: str = Field(..., max_length=255)
    begin_time: datetime
    end_time: datetime
    
    @validator('end_time')
    def validate_end_time(cls, v, values):
        if 'begin_time' in values and v <= values['begin_time']:
            raise ValueError("End time must be after begin time")
        return v

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    id: UUID4
    user_id: str
    viewers_count: int

    model_config = ConfigDict(from_attributes=True)

class OrderUpdate(OrderBase):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    price: Optional[float] = Field(None, gt=0)
    address: Optional[str] = Field(None, max_length=255)
    begin_time: Optional[datetime] = None
    end_time: Optional[datetime] = None