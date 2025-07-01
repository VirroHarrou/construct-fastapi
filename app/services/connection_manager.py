from datetime import datetime, timezone
from fastapi import WebSocket, HTTPException, WebSocketException, status
from fastapi.logger import logger
from pydantic import ValidationError
from sqlalchemy import UUID
from sqlalchemy.exc import SQLAlchemyError 
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chat_message import ChatMessage
from app.models.user import User
from app.schemas.users import UserResponse
from app.schemas.chat_messages import ChatMessageResponse, ChatMessageAction
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user: UserResponse):
        await websocket.accept()
        self.active_connections[user.id] = websocket

    def disconnect(self, user: UserResponse):
        if user.id in self.active_connections:
            del self.active_connections[user.id]

    async def handle_action(self, data: dict, user: UserResponse, db: AsyncSession):
        try:
            action = ChatMessageAction.model_validate(data)
            if action.action == "send":
                await self._handle_send(action, user, db)
            elif action.action == "edit":
                await self._handle_edit(action, user, db)
            elif action.action == "delete":
                await self._handle_delete(action, user, db)
                
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = " → ".join(map(str, error['loc']))
                msg = f"{field}: {error['msg']}"
                error_messages.append(msg)
            
            raise WebSocketException(
                code=status.WS_1003_UNSUPPORTED_DATA,
                reason=" | ".join(error_messages)
            )
            
    async def _handle_send(self, action: ChatMessageAction, user: UserResponse, db: AsyncSession):
        try:
            if not action.recipient_id or not action.content:
                raise WebSocketException(
                    code=status.WS_1003_UNSUPPORTED_DATA,
                    reason="Missing recipient_id or content"
                )

            recipient = await db.get(User, action.recipient_id)
            if not recipient:
                raise WebSocketException(
                    code=status.WS_1003_UNSUPPORTED_DATA,
                    reason="Recipient not found"
                )

            db_message = ChatMessage(
                message=action.content,
                sender_id=user.id,
                recipient_id=action.recipient_id
            )
            db.add(db_message)
            await db.commit()
            await self._send_response(db_message)

        except SQLAlchemyError as e:
            await db.rollback()
            raise WebSocketException(
                code=status.WS_1011_INTERNAL_ERROR,
                reason="Database error"
            )

    async def _handle_edit(self, action: ChatMessageAction, user: UserResponse, db: AsyncSession):
        if not action.message_id or not action.content:
            raise HTTPException(status_code=400, detail="Invalid request")
        
        message = await db.get(ChatMessage, action.message_id)
        
        if not message or message.sender_id != user.id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        message.message = action.content
        message.is_edited = True
        message.updated_at = datetime.now(timezone.utc)
        db.commit()
        await self._send_response(message)

    async def _handle_delete(self, action: ChatMessageAction, user: UserResponse, db: AsyncSession):
        message = await db.get(ChatMessage, action.message_id)
        
        if not message or message.sender_id != user.id:
            raise HTTPException(status_code=403, detail="Permission denied")
        
        message.is_deleted = True
        db.commit()
        await self._send_response(message)

    async def _send_response(self, message: ChatMessage):
        response = ChatMessageResponse.model_validate(message)
        recipient_ws = self.active_connections.get(message.recipient_id)
        sender_ws = self.active_connections.get(message.sender_id)
        
        if recipient_ws:
            await recipient_ws.send_text(response.model_dump_json())
        if sender_ws and message.sender_id != message.recipient_id:
            await sender_ws.send_text(response.model_dump_json())