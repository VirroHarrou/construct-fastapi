from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chat_message import ChatMessage
from app.models.user import User
from app.schemas.chat_messages import ChatListItem, ChatMessageResponse


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_chats(self, user_id: UUID) -> list[ChatListItem]:
        stmt = select(User).where(
            and_(
                or_(
                    User.id.in_(
                        select(ChatMessage.sender_id)
                        .where(ChatMessage.recipient_id == user_id)
                    ),
                    User.id.in_(
                        select(ChatMessage.recipient_id)
                        .where(ChatMessage.sender_id == user_id)
                    )
                ),
                ChatMessage.is_deleted != True
            )
        ).distinct()
        
        result = await self.db.execute(stmt)
        partners = result.scalars().all()
        
        chats = []
        for partner in partners:
            last_message_stmt = select(ChatMessage).where(
                and_(
                    ChatMessage.is_deleted != True,
                    or_(
                        and_(
                            ChatMessage.sender_id == user_id,
                            ChatMessage.recipient_id == partner.id
                        ),
                        and_(
                            ChatMessage.sender_id == partner.id,
                            ChatMessage.recipient_id == user_id
                        )
                    )
                )
            ).order_by(ChatMessage.created_at.desc()).limit(1)
            
            last_message_result = await self.db.execute(last_message_stmt)
            last_message = last_message_result.scalar_one_or_none()
            
            last_message_response = None
            if last_message:
                last_message_response = ChatMessageResponse.model_validate(last_message)
            
            chats.append(ChatListItem(
                id=partner.id,
                username=partner.fio,
                last_message=last_message_response
            ))
        
        return sorted(
            chats,
            key=lambda x: x.last_message.created_at if x.last_message else datetime.min,
            reverse=True
        )
    
    async def get_chat_history(
        self,
        user_id: UUID,
        partner_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> list[ChatMessageResponse]:
        stmt = select(ChatMessage).where(
            and_(
                ChatMessage.is_deleted != True,
                or_(
                    and_(
                        ChatMessage.sender_id == user_id,
                        ChatMessage.recipient_id == partner_id
                    ),
                    and_(
                        ChatMessage.sender_id == partner_id,
                        ChatMessage.recipient_id == user_id
                    )
                )
            )
        ).order_by(ChatMessage.created_at.desc()).offset(offset).limit(limit)
        
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        
        return [ChatMessageResponse.model_validate(msg) for msg in messages]