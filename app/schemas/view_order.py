from typing import Optional
from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator
    
class ViewOrderUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=24)
    user_id: Optional[UUID4]
    
    @field_validator('status')
    def validate_status(cls, v):
        allowed = [None, "ожидание", "в работе", "завершен"]
        if v not in allowed:
            raise ValueError(f"Invalid status. Allowed: {allowed}")
        return v