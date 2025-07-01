from pydantic import UUID4, BaseModel, ConfigDict, Field, field_validator, model_validator
from datetime import datetime

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ChatMessageAction(BaseModel):
    action: str  # send/edit/delete
    message_id: Optional[UUID4] = None
    content: Optional[str] = None
    recipient_id: Optional[UUID4] = None
    
    model_config = ConfigDict(
        extra='forbid',  
        validate_assignment=True 
    )
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        if v not in {'send', 'edit', 'delete'}:
            raise ValueError(
                "Invalid action type, it can take values: send, edit, delete"
            )
        return v

    @model_validator(mode='after')
    def validate_fields(self) -> 'ChatMessageAction':
        action = self.action
        
        if action in {'send', 'edit'} and not self.content:
            raise ValueError("The content field is required for this action.")
            
        if action == 'send' and self.recipient_id is None:
            raise ValueError("The recipient_id field is required for sending")
            
        if action in {'edit', 'delete'} and self.message_id is None:
            raise ValueError("The message_id field is required for this action.")
            
        return self

class ChatMessageResponse(BaseModel):
    id: UUID4
    content: str = Field(alias="message", serialization_alias="content")
    created_at: datetime
    updated_at: Optional[datetime]
    is_edited: bool
    is_deleted: bool
    sender_id: UUID4
    recipient_id: UUID4
    
    class Config:
        model_config = ConfigDict(from_attributes=True)
        from_attributes = True
        populate_by_name = True
        
class ChatListItem(BaseModel):
    id: UUID4
    username: str
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    
    class Config:
        model_config = ConfigDict(from_attributes=True)